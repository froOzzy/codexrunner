from django.urls import path

from codexrunner.views import (
    solving_the_task_view,
    categories_view,
    tasks_view,
    run_code,
    get_code_result,
    login_view,
)


urlpatterns = [
    path('codexrunner/api/v1/code/run/', run_code, name='run_code'),
    path('codexrunner/api/v1/code/result/', get_code_result, name='get_code_result'),
    path('category/<str:category_name>/task/<str:task_name>/', solving_the_task_view, name='solving_the_task_view'),
    path('category/', categories_view, name='categories_view'),
    path('category/<str:category_name>/task/', tasks_view, name='tasks_view'),
    path('login/', login_view, name='login_view'),
]
