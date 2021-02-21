import numpy as np

from cleverspeech.utils.Utils import l_map


def insert_target_blanks(target_indices):
    # get a shifted list so we can compare back one step in the phrase

    previous_indices = target_indices.tolist()
    previous_indices.insert(0, None)

    # insert blank tokens where ctc would expect them - i.e. `do-or`
    # also insert a blank at the start (it gives space for the RNN to "warm up")
    with_repeats = [28]
    for current, previous in zip(target_indices, previous_indices):
        if not previous:
            with_repeats.append(current)
        elif current == previous:
            with_repeats.append(28)
            with_repeats.append(current)
        else:
            with_repeats.append(current)
    return with_repeats


def gen_new_indices(new_target, n_feats, repeats):

    """
    Taking into account the space we have available, find out the new argmax
    indices for each frame of audio which relate to our target phrase

    :param new_target: the new target phrase included additional blank tokens
    :param n_feats: the number of features in the logits (time steps)
    :param repeats: the number of repeats for each token

    :return: the index for each frame in turn
    """

    spacing = n_feats // new_target.size

    for t in new_target:
        for i in range(spacing):
            if i > repeats:
                yield 28
            else:
                yield t


def add_kappa_to_all_logits(n_feats, n_padded_feats, example_logits, new_target, kappa, repeats):
    """
    Make the required modifications to the logits obtained from the original
    example.

    This search algorithm does:

    1. generate a vector with the desired argmax for our target phrase
    2. for each time step, increase the value of the desired character by kappa
    3. do any padding. N.B. this is never called for now.

    :param n_feats: number of features/time steps.
    :param n_padded_feats: number of features for the longest example in batch
    :param example_logits: the original logits for the current example
    :param new_target: the modified target phrase -- i.e. with extra blanks
    :param kappa: how much increase to apply to the logit values for characters
    :param repeats: how many repeated characters we want to insert

    :return: new logits for the current example which will now decode to the
    target phrase
    """
    padding = n_padded_feats - example_logits.shape[0]

    new_argmax = l_map(
        lambda x: x, gen_new_indices(new_target, n_feats, repeats)
    )

    for l, a in zip(example_logits, new_argmax):
        if np.argmax(l) == a:
            # where we our target character is already the most likely we don't
            # have to do any work
            # l[a] = l[a] + kappa
            pass
        else:
            # otherwise just increase the class we want by kappa
            l[a] = np.max(l) + kappa

    # we never actually call padding as we work out the appropriate length
    # based on the real number of features (not the batch's number of features).
    if padding > 0:
        padd_arr = np.zeros([29])
        padd_arr[28] = kappa
        padding = [padd_arr for _ in range(padding)]
        example_logits = np.concatenate([example_logits, np.asarray(padding)])

    return example_logits


def add_repeat_kappa_to_all_logits(n_feats, n_padded_feats, example_logits, new_target, kappas_dict, repeats):
    """
    Make the required modifications to the logits obtained from the original
    example.

    This search algorithm does:

    1. generate a vector with the desired argmax for our target phrase
    2. for each time step, increase the value of the desired character by kappa
    3. do any padding. N.B. this is never called for now.

    :param n_feats: number of features/time steps.
    :param n_padded_feats: number of features for the longest example in batch
    :param example_logits: the original logits for the current example
    :param new_target: the modified target phrase -- i.e. with extra blanks
    :param kappa: how much increase to apply to the logit values for characters
    :param repeats: how many repeated characters we want to insert

    :return: new logits for the current example which will now decode to the
    target phrase
    """
    padding = n_padded_feats - example_logits.shape[0]

    new_argmax = l_map(
        lambda x: x, gen_new_indices(new_target, n_feats, repeats)
    )

    for l, a in zip(example_logits, new_argmax):
        if np.argmax(l) == a:
            # where we our target character is already the most likely we don't
            # have to do any work
            # l[a] = l[a] + kappa
            pass
        else:
            # otherwise just increase the class we want by kappa
            l[a] = np.max(l) + kappas_dict[a]

    # we never actually call padding as we work out the appropriate length
    # based on the real number of features (not the batch's number of features).
    if padding > 0:
        padd_arr = np.zeros([29])
        padd_arr[28] = kappas_dict[28]
        padding = [padd_arr for _ in range(padding)]
        example_logits = np.concatenate(example_logits, np.asarray(padding))

    return example_logits