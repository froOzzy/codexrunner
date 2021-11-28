from django.db import models

from codexrunner.slug import slugify


class DateTimeMixin(models.Model):
    """Миксин для добавления дополнительных полей dt_created и dt_updated"""

    dt_created = models.DateTimeField(auto_now_add=True, editable=False, verbose_name='Дата создания')
    dt_updated = models.DateTimeField(auto_now=True, editable=False, verbose_name='Дата обновления')

    class Meta:
        """Метакласс"""

        abstract = True


class TaskCategory(DateTimeMixin):
    """Модель категорий задач"""

    name = models.CharField(max_length=200, verbose_name='Название категории')
    slug = models.CharField(max_length=200, editable=False)

    class Meta:
        """Метакласс"""

        verbose_name = 'Категория заданий'
        verbose_name_plural = 'Категории заданий'

    def __str__(self):
        """Отображение как строка"""
        return self.name

    def save(self, *args, **kwargs):
        """Метод сохранения объекта"""
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Task(DateTimeMixin):
    """Моедль для хранения задач с решением через код"""

    name = models.CharField(max_length=200, verbose_name='Название задачи')
    slug = models.CharField(max_length=200, editable=False)
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, verbose_name='Категория')
    task_text = models.TextField(max_length=50000, verbose_name='Текст задания в формате markdown/html')
    text_code_of_testing = models.TextField(
        max_length=50000,
        verbose_name='Текст кода теста для проверки решения (в формате Python)',
    )
    text_code_of_example = models.TextField(
        max_length=50000,
        verbose_name='Текст кода примера, который будет выведен как патерн выполнения задачи',
    )

    class Meta:
        """Метакласс"""

        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

    def __str__(self):
        """Отображение как строка"""
        return self.name

    def save(self, *args, **kwargs):
        """Метод сохранения объекта"""
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
