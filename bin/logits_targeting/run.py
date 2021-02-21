import os
import sys
import numpy as np
import tensorflow as tf

from cleverspeech.data import Feeds
from cleverspeech.data.etl import etls
from cleverspeech.data.etl import utils
from cleverspeech.data.etl.batch_generators import Batch
from cleverspeech.data.Results import SingleJsonDB
from cleverspeech.utils.Utils import log, l_map
from cleverspeech.utils.RuntimeUtils import TFRuntime, AttackSpawner

from SecEval import VictimAPI as DeepSpeech

from simple_branched_grid_search import branched_grid_search
from bisection_search import bisection_search
from character_branched_grid_search import per_char_branched_grid_search
from random_kappa_search import random_branched_grid_search

GPU_DEVICE = 0
MAX_PROCESSES = 1
SPAWN_DELAY = 15

INDIR = "./samples/all/"
TARGETS_PATH = "./samples/cv-valid-test.csv"
OUTDIR = "./target-logits/simple-branched-grid-search/"

TOKENS = " abcdefghijklmnopqrstuvwxyz'-"

BATCH_SIZE = 10
NUMB_EXAMPLES = 1000
MAX_AUDIO_LENGTH = 140000
TARGETS_POOL = 1000
AUDIO_EXAMPLES_POOL = 2000


def entropy(batch_softmaxes):
    return np.max(- np.sum(batch_softmaxes * np.log(batch_softmaxes), axis=1), axis=1)


def get_original_decoder_db_outputs(model, batch, feeds):
    """
    Get the decoding and transcription confidence score for the original example

    :param model: the model we attack, must have an inference() method
    :param batch: the batch of examples to try to generate logits for

    :return:
    """
    decodings, probs = model.inference(
        batch,
        feed=feeds.examples,
        decoder="batch",
        top_five=False
    )

    return decodings, probs


def get_original_network_db_outputs(model, batch, feeds):
    """
    Return the logits of the encoder (DeepSpeech's RNN).

    :param model: the model we attack, must have an inference() method
    :param batch: the batch of examples to try to generate logits for

    :return original_logits: the first set of logits we found.
    """

    logits, softmax = model.get_logits(
        [
            tf.transpose(model.raw_logits, [1, 0, 2]),
            model.logits
        ],
        feeds.examples
    )
    model.reset_state()

    return logits, softmax


def check_logits_variation(model, batch, feeds, original_logits):
    """
    Model is fixed and Logits should *never* change between inference calls for
    the same audio example. If it does then something is wrong.

    :param model: the model we attack, must have an inference() method
    :param batch: the batch of examples to try to generate logits for
    :param original_logits: the first set of logits we found.

    :return: Nothing.
    """
    logits, smax = get_original_network_db_outputs(
        model, batch, feeds
    )

    assert np.sum(logits - original_logits) == 0.0


def write_results(result):
    # TODO: skip later repeats if *NOTHING* was successful

    # store the db_outputs in a json file with the
    # absolute filepath *and* the original example as it
    # makes loading data for the actual optimisation attack
    # a hell of a lot easier
    if not os.path.exists(OUTDIR):
        os.mkdir(OUTDIR)

    # write out for each repeat value *and* the last success (is most confident)
    db_path = "{b}_targid-{t}_rep-{r}".format(
        b=result["audio_basename"].rstrip(".wav"),
        t=result["targ_id"],
        r=result["repeats"],
    )
    example_db = SingleJsonDB(OUTDIR)
    example_db.open(db_path).put(result)

    db_path = "{b}_targid-{t}_latest".format(
        b=result["audio_basename"].rstrip(".wav"),
        t=result["targ_id"],
    )
    example_db = SingleJsonDB(OUTDIR)
    example_db.open(db_path).put(result)

    # log how we've done
    s = "Success:    {b} for {r} repeats and target {t}".format(
        b=result["audio_basename"],
        r=result["repeats"],
        t=result["targ_id"],
    )
    s += " kappa: {k:.3f} orig score p.c.: {o:.1f} new score p.c.: {n:.1f}".format(
        k=result["kappa"],
        o=result["original_spc"],
        n=result["spc"],
    )
    s += " orig score : {o:.1f} new score: {n:.1f}".format(
        o=result["original_score"],
        n=result["score"],
    )
    s += " logits diff: {:.0f}".format(
        np.abs(np.sum(result["original_logits"] - result["new_logits"]))
    )
    s += " entropy: {}".format(
        entropy(result["new_softmax"])
    )

    s += " Wrote targeting data."
    log(s, wrap=False)


def run(results_queue, worker_conn, batch, search_type):

    tf_runtime = TFRuntime(0)

    with tf_runtime.session as sess, tf_runtime.device as tf_device:

        feeds = Feeds.Validation(batch)

        ph_examples = tf.placeholder(
            tf.float32, shape=[batch.size, batch.audios["max_samples"]]
        )
        ph_lens = tf.placeholder(
            tf.float32, shape=[batch.size]
        )

        model = DeepSpeech.Model(
            sess, ph_examples, batch, tokens=TOKENS, beam_width=500
        )

        feeds.create_feeds(
            ph_examples, ph_lens
        )

        original_decodings, original_probs = get_original_decoder_db_outputs(
            model, batch, feeds
        )

        real_logits, real_softmax = get_original_network_db_outputs(
            model, batch, feeds
        )

        for _ in range(10):
            check_logits_variation(
                model, batch, feeds, real_logits
            )

        worker_conn.send(True)

        if search_type == "sbgs":
            search_gen = branched_grid_search(
                INDIR,
                sess,
                model,
                batch,
                original_probs,
                real_logits,
            )

        elif search_type == "bisection":
            search_gen = bisection_search(
                INDIR,
                sess,
                model,
                batch,
                original_probs,
                real_logits,
            )

        elif search_type == "character":
            search_gen = per_char_branched_grid_search(
                INDIR,
                sess,
                model,
                batch,
                original_probs,
                real_logits,
            )
        elif search_type == "random":
            search_gen = random_branched_grid_search(
                INDIR,
                sess,
                model,
                batch,
                original_probs,
                real_logits,
            )
        else:
            search_gen = branched_grid_search(
                INDIR,
                sess,
                model,
                batch,
                original_probs,
                real_logits,
            )

        for idx, result in search_gen:
            write_results(result)


def main(search_type):

    # Create the factory we'll use to iterate over N examples at a time.
    attack_spawner = AttackSpawner(
        gpu_device=GPU_DEVICE,
        max_processes=MAX_PROCESSES,
        delay=SPAWN_DELAY,
        file_writer=None
    )

    with attack_spawner as spawner:

        all_audio_file_paths = etls.get_audio_file_path_pool(
            INDIR,
            AUDIO_EXAMPLES_POOL,
            file_size_sort="desc",
            filter_term=".wav",
            max_samples=MAX_AUDIO_LENGTH
        )

        all_transcriptions = etls.get_target_phrase_pool(
            TARGETS_PATH, TARGETS_POOL
        )

        log("New Run")

        for idx in range(0, AUDIO_EXAMPLES_POOL, BATCH_SIZE):

            # get n files paths and create the audio batch data
            audio_batch_data = utils.BatchGen.popper(all_audio_file_paths, BATCH_SIZE)
            audios_batch = etls.create_audio_batch(audio_batch_data)

            #  we need to make sure target phrase length < n audio feats.
            # also, the first batch should also have the longest target phrase
            # and longest audio examples so we can easily manage GPU Memory
            # resources with the AttackSpawner context manager.

            target_phrase = utils.BatchGen.pop_target_phrase(
                all_transcriptions, min(audios_batch["real_feats"])
            )

            # each target must be the same length else numpy throws a hissyfit
            # because it can't understand skewed matrices
            target_batch_data = l_map(
                lambda _: target_phrase, range(BATCH_SIZE)
            )

            # actually load the n phrases as a batch of target data
            targets_batch = etls.create_standard_target_batch(target_batch_data)

            batch = Batch(
                BATCH_SIZE,
                audios_batch,
                targets_batch,
            )

            spawner.spawn(run, batch, search_type)


if __name__ == '__main__':
    search_type = sys.argv[1]
    main(search_type)
