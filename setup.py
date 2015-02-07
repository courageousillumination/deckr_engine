from pip.req import parse_requirements
from setuptools import setup, find_packages

requirements = parse_requirements('requirements.txt')

setup(
    name = "deckr",
    version = "0.1",
    author = "Tristan Rasmussen",
    description = ("A simple engine for card and board games."),
    packages=find_packages(),
    scripts=['game_master'],
    install_requires=[str(ir.req) for ir in requirements]
)
