from django.views.decorators.http import require_GET
from django.shortcuts import render
from django.http import JsonResponse

from codexrunner.models import Task, TaskCategory


@require_GET
def get_the_tasks(request):
    """Отображение задач"""
    result = []
    tasks = Task.objects.all()
    for task in tasks:
        result.append({
            'name': task.name,
            'category_id': task.category_id,
            'task_text': task.task_text,
        })

    return JsonResponse(result, safe=False)


@require_GET
def get_the_categories(request):
    """Отображение категорий"""
    result = []
    categories = TaskCategory.objects.all()
    for category in categories:
        result.append({
            'name': category.name,
        })

    return JsonResponse(result, safe=False)


@require_GET
def solving_the_task(request):
    """Страница решения задачи"""
    return render(request, 'codexrunner/solving_task.html')
