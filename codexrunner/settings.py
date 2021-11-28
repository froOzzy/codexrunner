from django.conf import settings


DEFAULT_SETTINGS = {
    'IMAGE': {
        'NAME': 'codexrunner_image',
        'REQUIREMENTS_PATH': 'codexrunner/runner/image/requirements.txt',
        'DOCKERFILE_PATH': 'codexrunner/runner/'
    },
}
SETTINGS = getattr(settings, 'CODEXRUNNER_SETTINGS', DEFAULT_SETTINGS)
