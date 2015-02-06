from pip.req import parse_requirements
from setuptools import setup

requirements = parse_requirements('requirements.txt')

setup(
    name = "deckr",
    version = "0.1",
    author = "Tristan Rasmussen",
    description = ("A simple engine for card and board games."),
    packages=['deckr',
              'deckr.core',
              'deckr.networking',
              'deckr.contrib'],
    scripts=['game_master'],
    install_requires=[str(ir.req) for ir in requirements]
)
