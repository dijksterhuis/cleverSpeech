import os
import subprocess
from setuptools import setup


def get_info_from_plain_text(file_path):
    with open(file_path) as f:
        d = f.readlines()
    return d


def get_requirements_as_list(file_name):
    reqs = [r.rstrip("\n") for r in get_info_from_plain_text(file_name)]
    reqs = [x for x in reqs if len(x) != 0]
    reqs = [x for x in reqs if x[0] != "#"]
    reqs = [
        x.split("#egg=")[1] + " @ " + x if "git" in x else x for x in reqs
    ]
    return reqs


version = get_info_from_plain_text("./VERSION")[0]

try:
    subprocess.check_output("nvidia-smi")
except FileNotFoundError:
    nvidia_gpu = False
else:
    nvidia_gpu = True

# docker gpu image builds
for k in os.environ.keys():
    if "CUDA" in k or "NVIDIA" in k:
        nvidia_gpu = True

base_reqs_file_name = "./reqs-base.txt"
compute_reqs_file_name = "./reqs-gpu.txt" if nvidia_gpu else "./reqs-cpu.txt"

requirements = get_requirements_as_list(base_reqs_file_name)
requirements += get_requirements_as_list(compute_reqs_file_name)

script_grabbber_args = [
    "find",
    "./cleverspeech/scripts",
    "-path",
    "*.py",
    "-maxdepth",
    "1",
    "-type",
    "f",
]
script_paths = subprocess.check_output(script_grabbber_args)
script_paths = script_paths.decode().rstrip("\n").split("\n")
script_names = [x.split("/")[-1].replace("_", "-").rstrip(".py") for x in script_paths]
script_locs = [x.lstrip("./").rstrip(".py").replace("/", ".") for x in script_paths]

console_scripts = [
    "{n}={l}:main".format(n=x, l=y) for x, y in zip(script_names, script_locs)
]

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

setup(
    name='cleverSpeech',
    version=version,
    packages=packages,
    url='https://github.com/dijksterhuis/cleverSpeech',
    license='MIT License',
    install_requires=requirements,
    author='Mike Robeson',
    author_email='mrobeson@dundee.ac.uk',
    description='Generating adversarial examples for Mozilla DeepSpeech.',
    entry_points={
        "console_scripts": console_scripts
    }
)
