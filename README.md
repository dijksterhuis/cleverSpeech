# cleverSpeech

Code to generate adversarial examples (confidence/evasion attacks) for automatic speech recognition
models in tensorflow. Began as a modified version of [Carlini and Wagner's Attacks][0] against
[Mozilla STT][1].

Mainly used to prototype and evaluate attacks, so if you're looking for production ready code then
this might not be the repo for you.

This is the main repo used to create the released docker images. Everything is glued together with
git submodules (helps me to work on code in separation, rather than making major changes and causing
spaghetti code to fly everywhere).

If you want to see the package in action, grab a docker image or clone this repo using the steps
outlined below.

### cleverSpeech top-level project structure

- `.jenkins` contains the groovy script used by a local Jenkins instance to build and run experiments.
- `./bin/` contains shell scripts to get audio sample data and (hopefully) DeepSpeech data files.
- `./cleverspeech/` is the main package used to design and run attacks.
- `./docker/` contains the files needed to build docker images.
- [`./experiments/`](https://github.com/dijksterhuis/cleverspeech-exp) has all the definitions for
different attacks/experiments. Includes additional code for some experiments which extends the
`cleverspeech` package.
- `./models/` was originally meant to include a variety of models I was aiming to test but only
includes a [modified version of Mozilla DeepSpeech](https://github.com/dijksterhuis/DeepSpeechAdversary)
so far.

### `cleverspeech` package structure

The main API for building attacks is organised like so:
- [`cleverspeech.data`](https://github.com/dijksterhuis/cleverspeech-data) for loading data.
- [`cleverspeech.eval`](https://github.com/dijksterhuis/cleverspeech-eval) for evaluating attack success.
- [`cleverspeech.graph`](https://github.com/dijksterhuis/cleverspeech-graph) for building attack graphs (see `cleverspeech.graph.GraphConstructor` for more information).
- [`cleverspeech.utils`](https://github.com/dijksterhuis/cleverspeech-utils) for misc utils, like the parallel attack spawner.


## run the code

*N.B.*: These docker instructions are out of date as I'm in the middle of a big refactor.

Docker images are available [here](https://hub.docker.com/u/dijksterhuis/cleverspeech). The `latest`
tag image includes all experiments at their current point in development (basically dev/unstable).
`r*` tags are snapshots of the code when run for a specific experiment (e.g. for a
paper/thesis/workshop etc.).

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
4. Run one of the scripts from [`./experiments`](https://github.com/dijksterhuis/cleverspeech-exp)
```bash
python3 ./experiments/Baselines/attacks.py baseline
```

The `LOCAL_UID` and `LOCAL_GID` environment variables **must** be set. They're used to map file
permissions in `/home/cleverspeech` user to your current user, otherwise you have to mess around
with root file permission problems on any generated data.

Check out the `attacks.py` scripts for additional usage, especially pay attention to the `settings`
dictionaries, any `GLOBAL_VARS` (top of the scripts) and the `boilerplate.py` files. Feel free to
email me with any queries.

### don't like docker?

You're mad. But okay. Here's how this _should be installable_. Only tested on Ubuntu 18.04. Will
require `tensorflow-gpu` v1.13.1, so [make sure your GPU is setup
correctly](https://www.tensorflow.org/install/gpu#older_versions_of_tensorflow).

1. Run `git clone --recurse-submodules https://github.com/dijksterhuis/cleverSpeech.git`
2. Run `./install.sh`
3. Run an experiment, e.g. `python3 ./experiments/Baselines/attacks.py baseline`

TODO: Change the deepspeech-checkpoint paths to point at some download scripts in `./bin/`.

## current gotchas

**1**: Only 16 bit signed integer audio files are supported, i.e. mozilla common voice v1.

**2**: Integrity of the adversarial examples is an ongoing issue when using the
`deepspeech`/`deepspeech-gpu` python library (the one installed with `pip`). DeepSpeech source code
ingests `tf.float32` inputs `-2^15 <= x <= 2^15 -1` but the `deepspeech` library ingests 16-bit
integers, which breaks the attacks.

**3**: I run my experiments in sets (not batches!) of 10 examples. Adam struggles to optimise
as it's built for batch-wise learning rate tuning, but each of our examples are independent members
of a set (Lea Schoenherr's [recent paper][12] talks about this briefly).



## citations, licenses and sourced works

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
