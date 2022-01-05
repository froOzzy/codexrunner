# codexrunner
Django app for running Python code interview

## Settings

To configure it, it is enough to specify the data for connecting to django_rq in local_settings:

```python
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    },
    ...
}
```

You can also set the necessary settings of the package itself (example of default settings):

```python
DEFAULT_SETTINGS = {
    'IMAGE': {
        'NAME': 'codexrunner_image',
        'DOCKERFILE_PATH': absolute_path + '/runner/',
        'RUNNER_PATH': absolute_path + '/runner/image/cli_runner.py',
        'CONTAINER_WORKDIR': '/cli/',
        'PYPROJECT_TOML_PATH': absolute_path + '/runner/image/pyproject.toml',
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
```

After that, you need to build the Docker image using the command:

```bash
python3 manage.py codexrunner_build_image
```

And add a list of addresses to urls:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('codexrunner.urls')),
]

```

And finally perform migrations.

## Example

![Uploading изображение.png…]()

