import uuid
import time

from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.core.cache import cache

from rq import Queue

from codexrunner.models import Task, TaskCategory
from codexrunner.docker import start_container_of_parsing
from codexrunner.settings import SETTINGS
from codexrunner.redis_pool import redis_connection


@require_GET
def solving_the_task_view(request, category_name, task_name):
    """Страница решения задачи"""
    category = TaskCategory.objects.filter(slug=category_name).first()
    task = get_object_or_404(Task, category=category, slug=task_name)
    context = {
        'task': task,
        'category': category,
        'run_code_url': reverse('run_code'),
        'get_code_result_url': reverse('get_code_result'),
    }
    return render(request, 'codexrunner/solving_task.html', context=context)


@require_GET
def categories_view(request):
    """Страница категорий задач"""
    context = {
        'categories': TaskCategory.objects.all(),
    }
    return render(request, 'codexrunner/categories.html', context=context)


@require_GET
def tasks_view(request, category_name):
    """Страница задач"""
    category = TaskCategory.objects.filter(slug=category_name).first()
    context = {
        'tasks': Task.objects.filter(category=category),
        'category': category,
    }
    return render(request, 'codexrunner/tasks.html', context=context)


@require_POST
def run_code(request):
    """Метод для запуска кода на прогон через раннер"""
    text_code = request.POST.get('text_code')
    if not text_code:
        return JsonResponse(status=400, data={'message': 'Не код для запуска!'})

    task_name = request.POST.get('task_name')
    if not task_name:
        return JsonResponse(status=400, data={'message': 'Не задано название задачи!'})

    task = Task.objects.filter(slug=task_name).first()
    if not task:
        return JsonResponse(status=400, data={'message': 'Задача не найдена!'})

    try:
        queue = Queue(SETTINGS['RQ']['QUEUE_NAME'], default_timeout=35, connection=redis_connection())
        job_id = str(uuid.uuid4())
        params = {
            'f': start_container_of_parsing,
            'kwargs': {
                'answer_code': text_code,
                'test_code': task.text_code_of_testing,
                'run_timeout': 30,
            },
            'job_id': job_id,
        }
        job = queue.enqueue(**params)
        cache.set('codexrunner_job_{}'.format(job_id), job)
    except Exception as error:
        print(error)
        return JsonResponse(status=400, data={'message': 'Неудалось запустить задачу в очереди!'})

    return JsonResponse(status=200, data={'job_id': job_id})


@require_GET
def get_code_result(request):
    """Метод для получения результата выполнения кода"""
    job_id = request.GET.get('job_id')
    if not job_id:
        return JsonResponse(status=400, data={'message': 'Не найден job_id!'})

    job = cache.get('codexrunner_job_{}'.format(job_id))
    if not job:
        return JsonResponse(status=400, data={'message': 'Задача не найдена!'})

    return JsonResponse(status=200, data={'message': job.result})
