import uuid
import time
import json
import hashlib

from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.core.cache import cache

import django_rq

from codexrunner.models import Task, TaskCategory, User, UserRunTask
from codexrunner.docker import start_container_of_parsing
from codexrunner.settings import SETTINGS, RESULT_JOB_ID
from codexrunner.redis_pool import redis_connection


def authorization(function):
    """Декоратор для проверки авторизации"""
    def wrapper(*args, **kwargs):
        """Проверка всех требований"""
        request = args[0]
        session_id = request.session.get('codexrunner_session_id')
        user = cache.get(session_id)
        if user:
            user_progress_of_completed_tasks = 0
            user_tasks = user.tasks.all()
            user_completed_tasks = user.completed_tasks.all()
            if user.tasks.exists():
                user_progress_of_completed_tasks = user_completed_tasks.count() * 100 // user_tasks.count()

            setattr(request, 'codexrunner_user', user)
            setattr(request, 'codexrunner_user_progress_of_completed_tasks', user_progress_of_completed_tasks)
            setattr(request, 'codexrunner_user_tasks', user_tasks)
            setattr(request, 'codexrunner_user_completed_tasks', user_completed_tasks)
            return function(*args, **kwargs)

        return redirect('login_view')

    return wrapper


@require_GET
@authorization
def solving_the_task_view(request, category_name, task_name):
    """Страница решения задачи"""
    category = TaskCategory.objects.filter(slug=category_name).first()
    task = Task.objects.filter(category=category, slug=task_name).first()
    context = {
        'task': task,
        'category': category,
        'run_code_url': reverse('run_code'),
        'get_code_result_url': reverse('get_code_result'),
        'timeout_refresh_result': getattr(task, 'timeout_refresh_result', 0),
    }
    return render(request, 'codexrunner/solving_task.html', context=context)


@require_GET
@authorization
def categories_view(request):
    """Страница категорий задач"""
    context = {
        'categories': TaskCategory.objects.prefetch_related('task_set').filter(
            task__in=request.codexrunner_user_tasks,
        ).distinct(),
    }
    return render(request, 'codexrunner/categories.html', context=context)


@require_GET
@authorization
def tasks_view(request, category_name):
    """Страница задач по определенной категории"""
    tasks = list(request.codexrunner_user.tasks.filter(category__slug=category_name))
    context = {'tasks': [], 'category': None}
    if tasks:
        context = {
            'tasks': tasks,
            'category': tasks[0].category,
        }

    return render(request, 'codexrunner/tasks.html', context=context)


@require_POST
@authorization
def run_code(request):
    """Метод для запуска кода на прогон через раннер"""
    text_code = request.POST.get('text_code')
    if not text_code:
        return JsonResponse(status=400, data={'message': 'Не найден код для запуска!'})

    task_name = request.POST.get('task_name')
    if not task_name:
        return JsonResponse(status=400, data={'message': 'Не задано название задачи!'})

    task = request.codexrunner_user.tasks.filter(slug=task_name).first()
    if not task:
        return JsonResponse(status=400, data={'message': 'Задача не найдена!'})

    try:
        queue = django_rq.get_queue(
            SETTINGS['RQ']['QUEUE_NAME'],
            default_timeout=task.timeout_running_container + 10,
            connection=redis_connection()
        )
        job_id = str(uuid.uuid4())
        params = {
            'f': start_container_of_parsing,
            'kwargs': {
                'answer_code': text_code,
                'test_code': task.text_code_of_testing,
                'run_timeout': task.timeout_running_container,
                'job_id': job_id,
            },
            'job_id': job_id,
        }
        queue.enqueue(**params)
        UserRunTask.objects.create(
            job_id=job_id,
            user=request.codexrunner_user,
            task=task,
            code=text_code,
        )
    except Exception as error:
        return JsonResponse(status=400, data={'message': 'Неудалось запустить задачу в очереди!'})

    return JsonResponse(status=200, data={'job_id': job_id})


@require_GET
@authorization
def get_code_result(request):
    """Метод для получения результата выполнения кода"""
    job_id = request.GET.get('job_id')
    if not job_id:
        return JsonResponse(status=400, data={'message': 'Не найден job_id!'})

    user_run_task = UserRunTask.objects.filter(job_id=job_id).first()
    if not user_run_task:
        return JsonResponse(status=400, data={'message': 'Задача не была запущена!'})

    r_con = redis_connection()
    message_log = r_con.get(RESULT_JOB_ID.format(job_id))
    if not message_log:
        return JsonResponse(status=400, data={'message': 'Результат проверки не найден!'})

    data = json.loads(message_log)
    if not any(data.values()):
        request.codexrunner_user.completed_tasks.add(user_run_task)
        request.codexrunner_user.save()

    return JsonResponse(status=200, data=data)


def login_view(request):
    """Страница для авторизации"""
    if request.method == 'GET':
        return render(request, 'codexrunner/login.html')

    if request.method == 'POST':
        login = request.POST.get('login')
        password = request.POST.get('password')
        if not login or not password:
            return render(request, 'codexrunner/login.html', context={'error_message': 'Логин или пароль не найден!'})

        password = hashlib.blake2b(password.encode()).hexdigest()
        user = User.objects.filter(username=login, password=password).first()
        if not user:
            return render(request, 'codexrunner/login.html', context={'error_message': 'Неверный логин или пароль.'})

        if not user.is_active:
            return render(request, 'codexrunner/login.html', context={'error_message': 'Пользователь неактивен.'})

        session_id = str(uuid.uuid4())
        request.session['codexrunner_session_id'] = session_id
        cache.set(session_id, user, 12 * 60 * 60)
        return redirect('categories_view')

    return HttpResponse(status=400)


def logout_view(request):
    """Страница для выхода пользователя"""
    del request.session['codexrunner_session_id']
    return redirect('login_view')
