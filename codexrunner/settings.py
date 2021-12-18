from django.conf import settings


DEFAULT_SETTINGS = {
    'IMAGE': {
        'NAME': 'codexrunner_image',
        'REQUIREMENTS_PATH': 'codexrunner/runner/image/requirements.txt',
        'DOCKERFILE_PATH': 'codexrunner/runner/',
        'CONTAINER_WORKDIR': '/cli/',
    },
    'STAGES': [
        ('flakehell', 'flakehell lint'),
        ('bandit', 'bandit .'),
        ('pytest', 'pytest --showlocals'),
    ],
    'RQ': {
        'QUEUE_NAME': 'high',
    }
}
SETTINGS = getattr(settings, 'CODEXRUNNER_SETTINGS', DEFAULT_SETTINGS)
