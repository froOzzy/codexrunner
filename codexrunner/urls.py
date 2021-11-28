from django.urls import path

from codexrunner.views import get_the_tasks, get_the_categories, solving_the_task


urlpatterns = [
    path('codexrunner/api/v1/models/task/', get_the_tasks, name='get_the_tasks'),
    path('codexrunner/api/v1/models/category/', get_the_categories, name='get_the_categories'),
    path('', solving_the_task, name='solving_the_task'),
]
