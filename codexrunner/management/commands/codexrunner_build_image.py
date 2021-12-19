import subprocess

from django.core.management.base import BaseCommand

from codexrunner.settings import DEFAULT_SETTINGS, SETTINGS


class Command(BaseCommand):
    """Сборка образа"""

    help = 'Команда для сборки образа для теста корректного выполнения задания.'

    def add_arguments(self, parser):
        """Аргументы команды"""
        parser.add_argument('--dockerfile', type=str, default='')
        parser.add_argument('--name', type=str, default='')

    def handle(self, *args, **options):
        """Хендлер для запуска кода команды"""
        dockerfile_path = options.get('dockerfile') or SETTINGS.get('IMAGE', {}).get('DOCKERFILE_PATH')
        if not dockerfile_path:
            dockerfile_path = DEFAULT_SETTINGS['IMAGE']['DOCKERFILE_PATH']

        image_name = options.get('name') or SETTINGS.get('IMAGE', {}).get('NAME')
        if not image_name:
            image_name = DEFAULT_SETTINGS['IMAGE']['NAME']

        subprocess.run(['cd', dockerfile_path])
        subprocess.run(['docker', 'build', dockerfile_path, '--tag', image_name])
