import os
import re

from setuptools import setup, find_packages

version = os.environ.get('RULE_ENGINE_VERSION')
if not version:
    raise ValueError('RULE_ENGINE_VERSION is not set')

version = re.sub('^v', '', version)
if not re.match(r'^\d+\.\d+\.\d+$', version):
    raise ValueError(f'Invalid version: {version}')


def requires(filename='requirements.txt'):
    with open(filename) as f:
        return f.read().splitlines()


setup(
    name="cos-ruleengine",
    version=version,
    description="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requires(),
    extras_require={
        "dev": requires('requirements-dev.txt')
    },
    python_requires=">=3.7",
)
