import tensorflow as tf
import numpy as np
import os

from cleverspeech.utils.Utils import log, l_map
from utils import insert_target_blanks, gen_new_indices, add_kappa_to_all_logits, add_repeat_kappa_to_all_logits

TOKENS = " abcdefghijklmnopqrstuvwxyz'-"
MAX_REPEATS = 10
MAX_KAPPA = 9.0
MAX_DEPTH = 3


def bisection_search(indir, sess, model, batch, original_probs, real_logits):

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

            log("", wrap=True)

            s = "Processing: {b} for {r} repeats and target {t}".format(
                b=basename,
                r=current_repeat,
                t=targs_id
            )
            log(s, wrap=True)

            main_kappa = MAX_KAPPA

            big_kappa, small_kappa = main_kappa, -main_kappa
            current_depth = 1
            max_depth = 10 ** MAX_DEPTH

            result = {
                "kappa": main_kappa,
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
                "n_feats": n_feats,
                "targ_id": targs_id,
                "target_phrase": target_phrase,
                "new_target": new_target_phrases,
                "original_logits": real_logits[idx][:n_feats]
            }

            while current_depth <= max_depth:

                if len(new_target_phrases) * current_repeat > n_feats:
                    # repeats won't fit logits space so completely
                    # skip any further processing.
                    break

                else:
                    # otherwise, make some logits!
                    initial_logits = real_logits[idx].copy()

                    big_new_logits = add_kappa_to_all_logits(
                        n_feats,
                        n_padded_feats,
                        initial_logits,
                        new_target_phrases,
                        big_kappa,
                        current_repeat
                    )
                    small_new_logits = add_kappa_to_all_logits(
                        n_feats,
                        n_padded_feats,
                        initial_logits,
                        new_target_phrases,
                        small_kappa,
                        current_repeat
                    )

                big_new_logits = np.asarray([big_new_logits])
                small_new_logits = np.asarray([small_new_logits])

                # TODO: Test that only one character per frame has changed
                #  and the remainder are the same as before (i.e. diff = 0)

                # TODO: how can we escape the need to run as
                big_new_softmaxes = sess.run(
                    tf.nn.softmax(big_new_logits)
                )
                small_new_softmaxes = sess.run(
                    tf.nn.softmax(small_new_logits)
                )

                big_decodings, big_probs = model.inference(
                    batch,
                    logits=np.asarray(big_new_softmaxes),
                    decoder="ds",
                    top_five=False
                )
                small_decodings, small_probs = model.inference(
                    batch,
                    logits=np.asarray(small_new_softmaxes),
                    decoder="ds",
                    top_five=False
                )

                score_per_char = small_probs / len(target_phrase)

                # scores increase as the token probabilities get
                # closer. this seems counter intuitive, but it works

                big_correct = big_decodings == target_phrase
                small_correct = small_decodings == target_phrase

                both = big_correct and small_correct
                big = big_correct and not small_correct
                small = not big_correct and small_correct
                neither = not big_correct and not small_correct

                if both:

                    # edge case where we haven't set initial kappa high enough
                    # so both settings work

                    argmax = "".join(
                        l_map(
                            lambda x: TOKENS[x],
                            np.argmax(
                                big_new_logits[0][:n_feats],
                                axis=1
                            )
                        )
                    )

                    result["kappa"] = small_kappa
                    result["decoding"] = big_decodings
                    result["score"] = big_probs
                    result["spc"] = score_per_char
                    result["new_softmax"] = big_new_softmaxes[:n_feats]
                    result["new_logits"] = big_new_logits[0][:n_feats]
                    result["argmax"] = argmax

                if big_decodings != small_decodings \
                        and big_decodings == target_phrase \
                        and result["score"] < big_probs:

                    # great success!

                    best_kappa = main_kappa
                    kappa = main_kappa - 1 / current_depth
                    kappa = np.round(
                        kappa,
                        int(np.log10(max_depth))
                    )

                    # store the db_outputs
                    argmax = "".join(
                        l_map(
                            lambda x: TOKENS[x],
                            np.argmax(
                                big_new_logits[0][:n_feats],
                                axis=1
                            )
                        )
                    )

                    result["kappa"] = best_kappa
                    result["decoding"] = big_decodings
                    result["score"] = big_probs
                    result["new_softmax"] = big_new_softmaxes[:n_feats]
                    result["new_logits"] = big_new_logits[0][:n_feats]
                    result["argmax"] = argmax

                elif result["score"] != 0.0:
                    # we have been successful at some point, so
                    # reduce the search depth

                    d = current_depth * 10

                    # there's a weird bug where search depths
                    # become 0, and then kappa start to tend
                    # toward negative infinity, e.g.
                    # kappa: -0.11 -> -0.111 -> -0.11 -> -inf
                    if d == 0:
                        # something went wrong...
                        current_depth = max_depth

                    elif d > max_depth:
                        # we've hit the maximum, update depths,
                        # but don't update kappa
                        break

                    else:
                        # we're not at maximum search depth, so we
                        # must have just seen something good so
                        # change the depth and update kappa
                        current_depth = d
                        kappa = result["kappa"]
                        kappa = kappa - 1 / current_depth
                        kappa = np.round(
                            kappa,
                            int(np.log10(max_depth))
                        )

                elif kappa <= -MAX_KAPPA:
                    # we've hit a minimum boundary condition
                    break
                else:
                    # we haven't found anything yet
                    kappa = kappa - 1 / current_depth
                    kappa = np.round(
                        kappa,
                        int(np.log10(max_depth))
                    )

            if result["decoding"] != target_phrase:
                # we've not been successful, we probably won't
                # find anything useful by increasing the number of
                # repeats so break out of the loop
                break

            else:
                yield idx, result