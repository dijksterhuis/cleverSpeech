import os
import sys
import json
import numpy as np


def main(indir):
    file_paths = os.listdir(indir)

    results = {
        "max_logit": [],
        "min_logit": [],
        "max_other_logit": [],
        "mean_other_logit": [],
        "max_smax": [],
    }

    for file_path in sorted(file_paths):

        s = "Processing sample: {}\n".format(file_path)

        with open(os.path.join(indir, file_path), 'r') as f:
            data = json.load(f)[0]

        raw_logits = np.asarray(data["raw_logits"])
        softmax = np.asarray(data["smax_logits"])

        for idx, (raw_feats, smax_feats) in enumerate(zip(raw_logits, softmax)):

            results["max_logit"].append(np.max(raw_feats))
            results["min_logit"].append(np.min(raw_feats))

            other_logit = raw_feats[raw_feats < np.max(raw_feats)]
            results["max_other_logit"].append(np.max(other_logit))
            results["mean_other_logit"].append(np.mean(other_logit))

            results["max_smax"].append(np.max(smax_feats))

        #s += "Mean values over entire logits:\n"

        for k, v in results.items():
            mean = np.mean(v)
            s += "{k}: {v}\n".format(k=k, v=mean)

        s = s.replace("\n", ",")
        with open("./adv/original_logits_stats.csv", "a+") as f:
            f.write(s + "\n")

        for k in results.keys():
            results[k].clear()


if __name__ == '__main__':
    main(sys.argv[1])
