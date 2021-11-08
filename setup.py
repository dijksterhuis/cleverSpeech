from setuptools import setup
import os


def get_info_from_plain_text(file_path):
    with open(file_path) as f:
        d = f.readlines()
    return d


version = get_info_from_plain_text("./VERSION")[0]

requirements_file = "reqs-docker.txt" if "docker_build" in os.listdir("./") else "reqs.txt"
requirements = [r.rstrip("\n") for r in get_info_from_plain_text(requirements_file)]
requirements = [x for x in requirements if len(x) != 0]
requirements = [x for x in requirements if x[0] != "#"]
requirements = [x.split("#egg=")[1] + " @ " + x if "git" in x else x for x in requirements]

packages = [
    'cleverspeech',
    'cleverspeech.data',
    'cleverspeech.data.egress',
    'cleverspeech.data.metrics',
    'cleverspeech.data.ingress',
    'cleverspeech.data.utils',
    'cleverspeech.graph',
    'cleverspeech.graph.losses',
    'cleverspeech.graph.losses.adversarial',
    'cleverspeech.utils',
    'cleverspeech.config',
    'cleverspeech.runtime',
    'cleverspeech.models',
]

console_scripts = [
    "beam-path-attacks=cleverspeech.scripts.beam_search_path_attacks:main",
    "greedy-path-attacks=cleverspeech.scripts.greedy_search_path_attacks:main",
    "ctc-attacks=cleverspeech.scripts.ctc_attacks:main",
    "gradient-path-attacks=cleverspeech.scripts.gradient_path_attacks:main",
    "gpu_max_batch_size=cleverspeech.scripts.gpu_max_batch_size:main",
    "validate_examples=cleverspeech.scripts.validate:main",
]

setup(
    name='cleverSpeech',
    version=version,
    packages=packages,
    url='https://github.com/dijksterhuis/cleverSpeech',
    license='',
    install_requires=requirements,
    author='Mike Robeson',
    author_email='mrobeson@dundee.ac.uk',
    description='Generating adversarial examples for Mozilla DeepSpeech.',
    entry_points={
        "console_scripts": console_scripts
    }
)
