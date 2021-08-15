# cleverSpeech

Code to generate adversarial examples for [Mozilla STT][1].
Began as a modified version of [Carlini and Wagner's Attacks][0].

This is the build repo for docker images.
If you want to see the package in action, grab a docker image or clone this repo using the steps
outlined below.

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
4. Run one of the scripts from the [`./cleverspeech/scripts`](https://github.com/dijksterhuis/cleverspeech-py)
```bash
python3 ./cleverspeech/scripts/ctc-attacks.py --max_examples 1 --batch_size 1 --max_spawns 1
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

### don't like docker?

Run:
```bash
git clone --recurse-submodules \  # may take a while due to tensorflow submodule in DeepSpeech repo
  https://github.com/dijksterhuis/cleverSpeech.git \
  && cd ./cleverSpeech/ \
  && ./bin/install.sh \
  && python3 -m pip install -e .
```

Then run an experiment as before.

## citations, licenses and sourced works

TODO: Update licenses.

I've modified the following works, many thanks to the authors:
- [Carlini & Wagner][0]
- [Mozilla STT][1]


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
