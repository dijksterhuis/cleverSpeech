import os
import sys
import tensorflow as tf

from cleverspeech.data import Feeds
from cleverspeech.data.etl.batch_generators import get_validation_batch_generator
from cleverspeech.data.Results import SingleJsonDB
from cleverspeech.utils.Utils import log
from cleverspeech.utils.RuntimeUtils import TFRuntime

from SecEval import VictimAPI as DeepSpeech


def main(indir, tokens=" abcdefghijklmnopqrstuvwxyz'-"):

    # TODO: Load individual examples from JSON.

    # Create the factory we'll use to iterate over N examples at a time.

    settings = {
        "audio_indir": indir,
        "max_examples": None,
        "max_audio_file_bytes": None,
        "targets_path": "./samples/cv-valid-test.csv",
        "max_targets": 2000,
        "batch_size": 10,
        "gpu_device": 0,
    }

    batch_gen = get_validation_batch_generator(settings)

    for b_id, batch in batch_gen:

        tf_runtime = TFRuntime(settings["gpu_device"])
        with tf_runtime.session as sess, tf_runtime.device as tf_device:

            feeds = Feeds.Validation(batch)
            ph_examples = tf.placeholder(
                tf.float32, shape=[batch.size, batch.audios["max_samples"]]
            )
            ph_lens = tf.placeholder(
                tf.float32, shape=[batch.size]
            )
            model = DeepSpeech.Model(
                sess, ph_examples, batch, tokens=tokens, beam_width=500
            )
            feeds.create_feeds(ph_examples, ph_lens)

            decodings, probs = model.inference(
                batch,
                feed=feeds.examples,
                decoder="batch",
                top_five=False
            )

            raw, smax = sess.run(
                [
                    tf.transpose(model.raw_logits, [1, 0, 2]),
                    model.logits
                ],
                feed_dict=feeds.examples
            )

            outdir = "original-logits/"

            if not os.path.exists(outdir):
                os.mkdir(outdir)

            for idx, basename in enumerate(batch.audios["basenames"]):

                #TODO

                stats = {
                    "basename": basename,
                    "decoding": decodings[idx],
                    "score": probs[idx],
                    "raw_logits": raw[idx],
                    "softmax": smax[idx],
                    "size": batch.audios["n_samples"][idx],
                    "n_feats": batch.audios["real_feats"][idx],
                }

                example_db = SingleJsonDB(outdir)
                example_db.open(basename.rstrip(".wav")).put(stats)

                log("Processed file: {b}".format(b=basename), wrap=False)
                log("Decoding: {}".format(decodings[idx]), wrap=False)


if __name__ == '__main__':
    indir = sys.argv[1]
    main(indir)

