from django.contrib import admin
from codexrunner.models import TaskCategory, Task, User, UserRunTask


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


class UserAdmin(admin.ModelAdmin):
    """Админ панель для заданий"""

    list_display = ('username', 'is_active', 'dt_created', 'dt_updated')
    search_fields = ('username',)
    readonly_fields = ('dt_created', 'dt_updated')


admin.site.register(User, UserAdmin)


class UserRunTaskAdmin(admin.ModelAdmin):
    """Админ панель для логов выполнения заданий"""

    list_display = ('job_id', 'dt_created', 'dt_updated')
    search_fields = ('job_id',)
    readonly_fields = ('dt_created', 'dt_updated')


admin.site.register(UserRunTask, UserRunTaskAdmin)
