# cleverSpeech

Code to generate adversarial examples (confidence/synthesis based evasion attacks) for
[Mozilla STT][1]. Began as a modified version of [Carlini and Wagner's Attacks][0].

This is the main repo used to create the released docker images. Everything is glued together with
git submodules (helps me to work on code in separation, rather than making major changes and causing
spaghetti code to fly everywhere).

If you want to see the package in action, grab a docker image or clone this repo using the steps
outlined below.


### cleverSpeech top-level project structure

- `jenkins` contains the scripts used by a local Jenkins instance to build the docker images.
- `bin/` contains shell scripts to get audio sample data and DeepSpeech data files.
- [`cleverspeech/`](https://github.com/dijksterhuis/cleverspeech-py) is the main package used to
design and run experiments.
- `docker/` contains the files needed to build the docker images.
- [`experiments/`](https://github.com/dijksterhuis/cleverspeech-exp) has all the definitions for
different attacks/experiments. Includes additional code for some experiments which extend the
`cleverspeech` package.
- `models/` was originally meant to include a variety of models I was aiming to test but only
includes a [modified version of Mozilla DeepSpeech](https://github.com/dijksterhuis/DeepSpeechAdversary)
so far.

## run the code

Docker images are available [here](https://hub.docker.com/u/dijksterhuis/cleverspeech). The `latest`
tag image includes all experiments at their current point in development (basically dev/unstable).

To start running some experiments with docker:

1. Install the latest version of [docker][10] (at least version `19.03`).
2. Install and configure the [NVIDIA container runtime][8].
3. Run the container (the image itself will be pulled automatically):
```bash
docker run \
    -it \
    --rm \
    --name cleverspeech \
    --gpus all \
    dijksterhuis/cleverspeech:latest
```
4. Run one of the scripts from [`./experiments`](https://github.com/dijksterhuis/cleverspeech-exp)
```bash
python3 ./experiments/CTCBaselines/attacks.py ctc --max_examples 1 --batch_size 1 --max_spawns 1
```


If you want to run the container as your user and group ID you'll need to some extra arguments so
that the container can change the deepspeech checkpoint, language model, trie etc. file permissions:
```bash
# You will need to wait a few minutes for file permissions to propagate
docker run \
    -it \
    --rm \
    --name cleverspeech \
    --gpus all \
    -e LOCAL_UID=$(id -u ${USER}) \
    -e LOCAL_GID=$(id -g ${USER}) \
    -v path/to/output/dir:/home/cleverspeech/cleverSpeech/adv:rw \
    dijksterhuis/cleverspeech:latest
```

Check out the `attacks.py` scripts for additional usage, especially pay attention to the `settings`
dictionaries, any `GLOBAL_VARS` (top of the scripts) and the `boilerplate.py` files. Feel free to
email me with any queries.

### don't like docker?

You're mad, mad I tell you!

Anyway, here's how this _should_ be installable (rarely tested on Ubuntu 18.04). Will require
`tensorflow-gpu` v1.13.1, so [make sure your GPU is setup correctly](https://www.tensorflow.org/install/gpu#older_versions_of_tensorflow).

You'll also need to install the Mozilla DeepSpeech ctc decoder package manually. Checkout [this
section](https://github.com/dijksterhuis/cleverSpeech/blob/master/docker/Dockerfile.build#L54) of
`docker/Dockerfile.build`.

```bash
git clone --recurse-submodules https://github.com/dijksterhuis/cleverSpeech.git
cd ./cleverSpeech/ && ./bin/install.sh
. ./bin/attacks/env.sh
```

Then run an experiment:
```bash
python3 ./experiments/CTCBaselines/attacks.py ctc --max_examples 1 --batch_size 1 --max_spawns 1
```

## current gotchas

**1**: Only 16 bit signed integer audio files are supported, i.e. mozilla common voice v1.

**2**: The native client (`deepspeech`/`deepspeech-gpu` python package) ingests 16-bit
integers whereas the DeepSpeech source code ingests `tf.float32` inputs `-2^15 <= x <= 2^15 -1`.
This can break some attacks, but I've done my best to mitigate it.

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
