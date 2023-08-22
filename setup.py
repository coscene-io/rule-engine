import logging
import os
import re
from semver.version import Version

from setuptools import setup, find_packages

version = os.environ.get("RULE_ENGINE_VERSION")
if not version:
    logging.info("RULE_ENGINE_VERSION not set, might be running in CI")
    version = "0.0.0"

# Remove the leading "v" if present
version = re.sub("^v", "", version)
# Semantically check the version
version = str(Version.parse(version))


def requires(filename="requirements.txt"):
    with open(filename) as f:
        return f.read().splitlines()


setup(
    name="cos-ruleengine",
    version=version,
    description="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requires(),
    extras_require={"dev": requires("requirements-dev.txt")},
    python_requires=">=3.7",
)
