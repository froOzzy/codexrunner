from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='codexrunner',
    version='1.0',
    packages=['codexrunner'],
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'docker>=5.0.3',
        'Markdown>=3.3.6',
        'django-rq>=2.5.1',
        'docker>=5.0.3',
    ]
)

