import tarfile
import tempfile
import time
import inspect
from io import BytesIO
from multiprocessing.pool import ThreadPool
from multiprocessing.context import TimeoutError as MultiprocessingTimeoutError

import docker
from django.core.cache import cache

from codexrunner.settings import SETTINGS, RESULT_JOB_ID
from codexrunner.redis_pool import redis_connection


def run_with_timeout(
    func,  # noqa: ANN001
    func_args=None,
    func_kwargs=None,
    timeout: int = 10,
):
    """
    Функция для запуска других функций с заданным таймаутом
    В случае, когда функция не выполняется за отведенное время
    выкидывается multiprocessing.context.TimeoutError
    :param func: запускаемая функция
    :param func_args: параметры функции
    :param func_kwargs: параметры функции
    :param timeout: время на выполнение функции
    :return: результат выполнения функции
    """
    if not func_args:
        func_args = ()

    if not func_kwargs:
        func_kwargs = {}

    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(func, func_args, func_kwargs)
    return async_result.get(timeout)


def copy_to_docker(container, path: str, filename: str, data: str):
    """
    Функция для копирования данных в контейнер докера
    :param container: объект контейнера
    :param path: путь до файла в контейнере
    :param filename: имя файла в контейнере
    :param data: сохраняемые данные
    :return:
    """
    with tempfile.TemporaryFile(suffix='.tar') as temp_archive:
        with tarfile.open(fileobj=temp_archive, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=filename)
            encode_data = data.encode()
            tarinfo.size = len(encode_data)
            tarinfo.mtime = time.time()  # type: ignore
            tar.addfile(tarinfo, BytesIO(encode_data))

        temp_archive.flush()
        temp_archive.seek(0)
        container.put_archive(path, temp_archive)

    return container


def start_container_of_parsing(
    answer_code: str,
    test_code: str,
    run_timeout: int,
    job_id: str,
) -> None:
    """
    Функция для запуска контейнера
    :param run_timeout: таймаут
    :param answer_code: код ответа
    :param test_code: код теста
    :param job_id: идентификатор задачи
    """
    r_con = redis_connection()
    try:
        container_path = SETTINGS['IMAGE']['CONTAINER_WORKDIR']
        run_command = 'python3 runner.py'
        docker_client = docker.from_env()
        container = docker_client.containers.create(
            SETTINGS['IMAGE']['NAME'],
            tty=True,
            auto_remove=False,
        )
        with open(SETTINGS['IMAGE']['RUNNER_PATH']) as file:
            runner = file.read()

        with open(SETTINGS['IMAGE']['PYPROJECT_TOML_PATH']) as file:
            pyproject_toml = file.read()

        copy_to_docker(container, container_path, 'answer.py', answer_code)
        copy_to_docker(container, container_path, 'tests.py', test_code)
        copy_to_docker(container, container_path, 'runner.py', runner)
        copy_to_docker(container, container_path, 'settings.py', 'STAGES = {}'.format(SETTINGS['STAGES']))
        copy_to_docker(container, container_path, 'pyproject.toml', pyproject_toml)
        command_params = {
            'cmd': run_command,
            'workdir': container_path,
        }
        container.start()
        try:
            log = run_with_timeout(container.exec_run, func_kwargs=command_params, timeout=run_timeout)
            message_log = log.output.decode()
        except MultiprocessingTimeoutError:
            message_log = 'Выполнение упало по таймауту!'
        finally:
            container.stop()
            container.remove()
    except Exception as error:
        message_log = error

    r_con.set(RESULT_JOB_ID.format(job_id), message_log, ex=30 * 60)
