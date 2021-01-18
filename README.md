# cleverSpeech

Classes/modules I use to generate adversarial examples for automatic speech recognition models in
tensorflow. Began as a modified version of [Carlini and Wagner's Attacks][0] against
[Mozilla STT][1].

Mainly used to prototype and evaluate attacks, so if you're looking for production ready code then
this is not the repo for you.

If you're looking for the experiments I've run as part of my PhD, then head over to the
[cleverSpeechExperiments](https://github.com/dijksterhuis/cleverSpeechExperiments) repo.

## Run the code

*N.B.*: I'm in the middle of a big refactor, so these docker instructions are out of date.

Docker images are available [here](https://hub.docker.com/u/dijksterhuis/cleverspeech).

The `latest` or `experiment` tags include the experiments I've run for my PhD work as part of the
[cleverSpeechExperiments](https://github.com/dijksterhuis/cleverSpeechExperiments) repo.
The `build` tag is the basic image with _only_ the
[cleverSpeech](https://github.com/dijksterhuis/cleverSpeech) repo included.

My work is packaged with docker so that:
1. You don't have to go through the same dependency hell I went through.
2. You don't have to worry about getting the right data, checkpoints, commits etc.
3. You can validate my results with the exact set-up I had by running one/two commands.

To start running some experiments with docker:

1. Install the latest version of [docker][10] (at least version `19.03`).
2. Install and configure the [NVIDIA container runtime][8].
3. Run the container (the image itself will be pulled automatically):
```bash
docker run \
    -it \
    --rm \
    --gpus all \
    -e LOCAL_UID=$(id -u ${USER}) \
    -e LOCAL_GID=$(id -g ${USER}) \
    -v path/to/original/samples/dir:/home/cleverspeech/cleverSpeech/samples:ro \
    -v path/to/output/dir:/home/cleverspeech/cleverSpeech/adv:rw \
    dijksterhuis/cleverspeech:latest
```
4. Run one of the scripts from [cleverSpeechExperiments](https://github.com/dijksterhuis/cleverSpeechExperiments)
```bash
python3 ./experiments/Baselines/attacks.py baseline
```

The `LOCAL_UID` and `LOCAL_GID` environment variables must be set. They're used to map file
permissions in `/home/cleverspeech` user to your current user, otherwise you have to mess around
with root file permission problems on any generated data.

Check out the `attacks.py` scripts for additional usage, especially pay attention to the `settings`
dictionaries, any `GLOBAL_VARS` (top of the scripts) and the `boilerplate.py` files. Feel free to
email me with any queries.

### Non-Docker Usage

Only tested on Ubuntu 18.04. Will require `tensorflow-gpu`, so make sure your GPU is setup
correctly.

1. Run `git clone --recurse-submodules https://github.com/dijksterhuis/cleverSpeech.git`
2. Run `./install.sh`
3. Run an experiment, e.g. `python3 ./experiments/Baselines/attacks.py baseline`

### Citations / Licenses / Sourced Works

TODO: Update licenses.

I've modified the following works, many thanks to the authors:
- [Carlini & Wagner][0]
- [Mozilla STT][1]
- [magneta/ddsp][4]

I use these extra modules:
- [p3nvml](https://github.com/fbcotter/py3nvml)
- [waveform_analysis](https://github.com/endolith/waveform_analysis)


[0]: https://arxiv.org/abs/1801.01944
[1]: https://github.com/mozilla/STT
[2]: https://arxiv.org/abs/1608.04644
[3]: https://arxiv.org/abs/1712.03141
[4]: https://github.com/magenta/ddsp
[5]: https://arxiv.org/abs/1902.06705
[6]: https://hub.docker.com/r/dijksterhuis/cleverspeech
[7]: https://github.com/dijksterhuis/cleverSpeech/packages
[8]: https://github.com/NVIDIA/nvidia-container-runtime
[9]: https://whoami.dijksterhuis.co.uk
[10]: https://docker.com
[11]: https://github.com/dijksterhuis/cleverSpeech/packages/336838
[12]: https://arxiv.org/abs/2005.14611
