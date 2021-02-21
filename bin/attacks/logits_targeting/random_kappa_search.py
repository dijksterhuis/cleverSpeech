import tensorflow as tf
import numpy as np
import os

from cleverspeech.utils.Utils import log, l_map
from utils import insert_target_blanks, gen_new_indices, add_kappa_to_all_logits, add_repeat_kappa_to_all_logits

TOKENS = " abcdefghijklmnopqrstuvwxyz'-"
MAX_REPEATS = 10
MAX_KAPPA = 4.0
MAX_DEPTH = 3
BEAM_WIDTH = 100





def random_branched_grid_search(indir, sess, model, batch, original_probs, real_logits):

    for idx in range(batch.size):

        basename = batch.audios["basenames"][idx]
        target_phrase = batch.targets["phrases"][idx]
        indices = batch.targets["indices"][idx]
        n_padded_feats = batch.audios["ds_feats"][idx]
        n_feats = batch.audios["real_feats"][idx]
        targs_id = batch.targets["row_ids"][idx]
        original_audio = batch.audios["audio"][idx]
        absolute_file_path = os.path.abspath(
            os.path.join(indir, basename)
        )

        new_target_phrases = np.array(
            insert_target_blanks(indices)
        )

        for current_repeat in range(MAX_REPEATS):

            # s = "Processing: {b} for {r} repeats and target {t}".format(
            #     b=basename,
            #     r=current_repeat,
            #     t=targs_id
            # )
            # log(s, wrap=False)

            if len(new_target_phrases) * current_repeat > n_feats:
                # repeats won't fit logits space so completely
                # skip any further processing.
                s = "Skipping:   {b} for {r} repeats and target {t}".format(
                    b=basename,
                    r=current_repeat,
                    t=targs_id
                )
                s += " (not enough space for all repeated characters)."
                log(s, wrap=False)

                break

            kappas = np.random.uniform(-MAX_KAPPA, MAX_KAPPA, BEAM_WIDTH)

            result = {
                "kappa": None,
                "decoding": None,
                "score": 0.0,
                "new_logits": None,
                "new_softmax": None,
                "argmax": None,
                "audio_filepath": absolute_file_path,
                "audio_basename": basename,
                "audio_data": original_audio,
                "repeats": current_repeat,
                "original_score": original_probs[idx],
                "original_spc": original_probs[idx] / len(target_phrase),
                "n_feats": n_feats,
                "targ_id": targs_id,
                "target_phrase": target_phrase,
                "new_target": new_target_phrases,
                "original_logits": real_logits[idx][:n_feats]
            }

            for kappa in kappas:

                # make some logits!
                initial_logits = real_logits[idx].copy()

                new_logits = add_kappa_to_all_logits(
                    n_feats,
                    n_padded_feats,
                    initial_logits,
                    new_target_phrases,
                    kappa,
                    current_repeat
                )

                new_logits = np.asarray([new_logits])

                # TODO: Test that only one character per frame has changed
                #  and the remainder are the same as before (i.e. diff = 0)

                # TODO: how can we escape the need to run as
                new_softmaxes = sess.run(
                    tf.nn.softmax(new_logits)
                )

                decodings, probs = model.inference(
                    batch,
                    logits=np.asarray(new_softmaxes),
                    decoder="ds",
                    top_five=False
                )

                score_per_char = probs / len(target_phrase)

                # s = "\r"
                # s += "Current kappa: {}".format(kappa)
                # s += "\tCurrent probs: {}".format(probs)
                # s += "\t"
                # s += "\tCurrent Depth: "+"\t".join(
                #         l_map(lambda x: str(x), new_search_depth)
                #     )
                # sys.stdout.write(s)
                # sys.stdout.flush()

                # scores increase as the token probabilities get
                # closer. this seems counter intuitive, but it works

                if decodings == target_phrase and result["score"] < probs:

                    # great success!

                    best_kappa = kappa

                    # store the db_outputs
                    argmax = "".join(
                        l_map(
                            lambda x: TOKENS[x],
                            np.argmax(
                                new_logits[0][:n_feats],
                                axis=1
                            )
                        )
                    )

                    result["kappa"] = best_kappa
                    result["decoding"] = decodings
                    result["score"] = probs
                    result["spc"] = score_per_char
                    result["new_softmax"] = new_softmaxes[:n_feats]
                    result["new_logits"] = new_logits[0][:n_feats]
                    result["argmax"] = argmax [:n_feats]

                elif result["score"] != 0.0:
                    # we have been successful at some point
                    pass

                else:
                    # we haven't found anything yet
                    continue

            if result["decoding"] != target_phrase:
                # we've not been successful, we probably won't
                # find anything useful by increasing the number of
                # repeats so break out of the loop
                s = "Failure:    {b} for {r} repeats and target {t}".format(
                    b=result["audio_basename"],
                    r=result["repeats"],
                    t=result["targ_id"],
                )
                log(s, wrap=False)
                break

            else:
                yield idx, result

