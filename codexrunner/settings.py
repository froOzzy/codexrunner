from django.conf import settings


DEFAULT_SETTINGS = {
    'IMAGE': {
        'NAME': 'codexrunner_image',
        'DOCKERFILE_PATH': 'codexrunner/runner/',
        'CONTAINER_WORKDIR': '/cli/',
        'PYPROJECT_TOML_PATH': '/runner/image/pyproject.toml',
    },
    'STAGES': [
        ('flakehell', 'python3 -m flakehell lint answer.py --format=gitlab --output-file flakehell.json'),
        ('bandit', 'python3 -m bandit -r answer.py -q -f json -o bandit.json --ignore-nosec'),
        (
            'pytest',
            'python3 -m pytest --json-report --json-report-file=pytest.json -v tests.py -q --disable-warnings -s',
        ),
    ],
    'RQ': {
        'QUEUE_NAME': 'default',
    }
}
SETTINGS = getattr(settings, 'CODEXRUNNER_SETTINGS', DEFAULT_SETTINGS)
RESULT_JOB_ID = 'codexrunner_result_job_{}'
