from django.contrib import admin
from codexrunner.models import TaskCategory, Task


class TaskCategoryAdmin(admin.ModelAdmin):
    """Админ панель для категорий заданий"""

    list_display = ('name', 'dt_created', 'dt_updated')
    search_fields = ('name',)
    readonly_fields = ('dt_created', 'dt_updated')


admin.site.register(TaskCategory, TaskCategoryAdmin)


class TaskAdmin(admin.ModelAdmin):
    """Админ панель для заданий"""

    list_display = ('name', 'category', 'dt_created', 'dt_updated')
    search_fields = ('name',)
    readonly_fields = ('dt_created', 'dt_updated')


admin.site.register(Task, TaskAdmin)
