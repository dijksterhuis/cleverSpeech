import tensorflow as tf
import numpy as np
import os

from copy import deepcopy
from cleverspeech.utils.Utils import log, l_map
from utils import insert_target_blanks, gen_new_indices, add_kappa_to_all_logits, add_repeat_kappa_to_all_logits


TOKENS = " abcdefghijklmnopqrstuvwxyz'-"
MAX_KAPPA = 20
MAX_DEPTH = 3


def per_char_branched_grid_search(indir, sess, model, batch, original_probs, real_logits):

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
        current_repeat = 2

        #while current_repeat * len(new_target_phrases) <= n_feats:

        if n_feats < len(new_target_phrases):
            s = "Skipping:   {b} for {r} repeats and target {t}".format(
                b=basename,
                r=current_repeat,
                t=targs_id
            )
            s += " (not enough space)."
            log(s, wrap=False)

        else:
            current_repeat = n_feats // len(new_target_phrases)

            new_indices = np.asarray(
                l_map(
                    lambda x: x,
                    gen_new_indices(
                        new_target_phrases,
                        n_feats,
                        current_repeat
                    )
                ),
                dtype=np.int16
            )

            # s = "Processing: {b} for {r} repeats and target {t}".format(
            #     b=basename,
            #     r=current_repeat,
            #     t=targs_id
            # )
            # log(s, wrap=False)

            kappa = 0
            current_depth = 1
            max_depth = 10 ** MAX_DEPTH

            result = {
                "kappa": kappa,
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

            alignment = deepcopy(real_logits[idx])

            for char_idx, character in enumerate(new_target_phrases):

                for repeat_idx in range(0, current_repeat):
                    alignment_idx = char_idx * current_repeat + repeat_idx
                    print("IDX: ", alignment_idx, "NFEATS: ", n_feats)

                    subseq_diff = np.max(alignment[alignment_idx]) - np.min(alignment[alignment_idx])
                    subseq_diff = np.abs(subseq_diff)
                    subseq_diff = (np.round(subseq_diff) // 5) + 5

                    kappa = 0

                    while kappa <= subseq_diff:

                        # make some logits!

                        alignment[alignment_idx:, character] += 5

                        #print(alignment, subsequence)

                        new_logits = np.asarray([alignment])

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

                        # decodings = model.tf_beam_decode(
                        #     sess,
                        #     tf.transpose(new_logits, [1, 0, 2]),
                        #     [n_feats],
                        #     TOKENS
                        # )[0]
                        if char_idx == 28:
                            current_character_decode = decodings[:char_idx - 1]
                            current_character_target = target_phrase[:char_idx - 1]
                        else:
                            current_character_decode = decodings[:char_idx]
                            current_character_target = target_phrase[:char_idx]

                        # print(
                        #     character,
                        #     kappa,
                        #     new_logits.shape,
                        #     alignment.shape,
                        #     element.shape,
                        #     current_character_decode,
                        #     "|",
                        #     current_character_target,
                        #     #subsequence
                        # )

                        if current_character_decode == current_character_target:
                            # print("OOOOOOOOOOOO YEAH")
                            kappa = subseq_diff + 1

                        else:
                            kappa += 5

                print("current probs : {p:.1f} decode: {d}".format(p=probs, d=decodings[:char_idx]))
                print("previous score: {p:.1f} target: {d} ".format(p=original_probs[idx], d=target_phrase[:char_idx]))

            print("decode: ", decodings)
            print("target: ", target_phrase)
            print("probs", probs)

