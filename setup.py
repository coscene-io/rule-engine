from setuptools import setup, find_packages


def requires(filename='requirements.txt'):
    with open(filename) as f:
        return f.read().splitlines()


setup(
    name="cos-ruleengine",
    version="0.1.3",
    description="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requires(),
    python_requires=">=3.7",
)
