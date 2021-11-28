from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='codexrunner',
    version='1.0',
    packages=['codexrunner'],
    long_description=open(join(dirname(__file__), 'README.md')).read(),
)

