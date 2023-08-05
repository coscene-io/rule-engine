from setuptools import setup, find_packages


def requires(filename='requirements.txt'):
    with open(filename) as f:
        return f.read().splitlines()


setup(
    name="ruleengine",
    version="0.1.0",
    description="",
    packages=find_packages(include=["ruleengine", "ruleengine.*"]),
    install_requires=requires(),
    python_requires=">=3.7",
)
