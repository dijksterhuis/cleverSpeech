import tensorflow as tf
import numpy as np
import os

from cleverspeech.utils.Utils import log, l_map
from utils import insert_target_blanks, gen_new_indices, add_kappa_to_all_logits, add_repeat_kappa_to_all_logits

TOKENS = " abcdefghijklmnopqrstuvwxyz'-"
MIN_KAPPA = -5.0
MAX_DEPTH = 3


def update_kappa(kappa, current_depth, max_depth):
    kappa = kappa + 1 / current_depth
    kappa = np.round(kappa, int(np.log10(max_depth)))
    return kappa


def branched_grid_search(indir, sess, model, batch, original_probs, real_logits, reference=np.max):

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
            insert_target_blanks(indices),
            dtype=np.int32
        )
        max_repeats = n_feats // len(new_target_phrases)
        for current_repeat in range(0, max_repeats):

            # s = "Processing: {b} for {r} repeats and target {t}".format(
            #     b=basename,
            #     r=current_repeat,
            #     t=targs_id
            # )
            # log(s, wrap=False)

            kappa = MIN_KAPPA
            current_depth = 1
            max_depth = 10 ** MAX_DEPTH

            result = {
                "kappa": kappa,
                "decoding": None,
                "score": float('inf'),
                "spc": float('inf'),
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

            while current_depth <= max_depth:

                if len(new_target_phrases) * current_repeat > n_feats:
                    # repeats won't fit logits space so completely
                    # skip any further processing.
                    break

                else:
                    # otherwise, make some logits!
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

                # scores increase as the token probabilities get
                # closer. this seems counter intuitive, but it works

                current_decoding_correct = decodings == target_phrase
                current_score_better = result["spc"] > score_per_char
                best_score_non_zero = result["score"] != float('inf')

                if current_decoding_correct and current_score_better:

                    # great success!
                    best_kappa = kappa
                    kappa = update_kappa(kappa, current_depth, max_depth)

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

                elif best_score_non_zero:
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
                        kappa = update_kappa(kappa, current_depth, max_depth)

                # elif kappa >= MIN_KAPPA:
                #     # we've hit a boundary condition
                #     break
                else:
                    # we haven't found anything yet
                    kappa = update_kappa(kappa, current_depth, max_depth)

            best_decoding_check = result["decoding"] != target_phrase
            best_spc_check = result["spc"] >= result["original_spc"]

            if best_decoding_check:
                # we've not been successful, increase the number of repeats
                # and try again
                s = "Failure:    {b} for {r} repeats and target {t}".format(
                    b=result["audio_basename"],
                    r=result["repeats"],
                    t=result["targ_id"],
                )
                s += " (decoding does not match target phrase)."
                log(s, wrap=False)

            elif best_spc_check:
                # we've not been successful, increase the number of repeats
                # and try again
                s = "Failure:    {b} for {r} repeats and target {t}".format(
                    b=result["audio_basename"],
                    r=result["repeats"],
                    t=result["targ_id"],
                )
                s += " adversarial score per char. <= original score per char.:"
                s += " {a:.1f} vs. {b:.1f}".format(
                    a=result["spc"],
                    b=result["original_spc"]
                )
                log(s, wrap=False)

            else:
                yield idx, result


