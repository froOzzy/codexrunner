from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='codexrunner',
    version='1.0',
    packages=[
        'codexrunner',
        'codexrunner.management',
        'codexrunner.management.commands',
        'codexrunner.migrations',
        'codexrunner.runner',
        'codexrunner.runner.image',
        'codexrunner.static',
        'codexrunner.static.codexrunner',
        'codexrunner.static.codexrunner.bootstrap5',
        'codexrunner.static.codexrunner.codemirror',
        'codexrunner.static.codexrunner.jquery',
        'codexrunner.templates',
        'codexrunner.templates.codexrunner',
        'codexrunner.templatetags',
    ],
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'docker>=5.0.3',
        'Markdown>=3.3.4',
        'django-rq>=2.4.1',
    ],
    include_package_data=True,
)

