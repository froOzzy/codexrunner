import hashlib

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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
    description = models.TextField(max_length=1000, verbose_name='Описание категории')

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
    description = models.TextField(max_length=1000, verbose_name='Описание задачи')
    task_text = models.TextField(max_length=50000, verbose_name='Текст задания в формате markdown/html')
    text_code_of_testing = models.TextField(
        max_length=50000,
        verbose_name='Текст кода теста для проверки решения (в формате Python)',
    )
    text_code_of_example = models.TextField(
        max_length=50000,
        verbose_name='Текст кода примера, который будет выведен как патерн выполнения задачи',
    )
    timeout_running_container = models.IntegerField(
        verbose_name='Таймаут для запуска контейнера',
        default=30,
        validators=[MaxValueValidator(10000), MinValueValidator(0)],
    )
    timeout_refresh_result = models.IntegerField(
        verbose_name='Таймаут на получение результата проверки',
        default=30,
        validators=[MaxValueValidator(10000), MinValueValidator(0)],
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


class User(DateTimeMixin):
    """Модель пользователей"""

    username = models.CharField(unique=True, verbose_name='Логин', max_length=200)
    password = models.CharField(verbose_name='Пароль', max_length=128)
    is_active = models.BooleanField(default=True, verbose_name='Активность пользователя')
    tasks = models.ManyToManyField(Task, verbose_name='Доступные задания', blank=True)
    completed_tasks = models.ManyToManyField(
        Task,
        verbose_name='Выполненные задания',
        blank=True,
        related_name='completed_tasks',
    )

    class Meta:
        """Метакласс"""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Отображение как строка"""
        return self.username

    def save(self, *args, **kwargs):
        """Метод сохранения объекта"""
        if getattr(self, 'id', None):
            user = User.objects.get(id=self.id)
            if user.password != self.password:
                self.password = hashlib.blake2b(self.password.encode()).hexdigest()
        else:
            self.password = hashlib.blake2b(self.password.encode()).hexdigest()

        super().save(*args, **kwargs)


class UserRunTask(DateTimeMixin):
    """Модель для хранения истории запуска кода"""

    job_id = models.UUIDField(editable=False, verbose_name='Идентификатор задачи')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='Задача')
    code = models.TextField(max_length=50000, verbose_name='Код пользователя')

    class Meta:
        """Метакласс"""

        verbose_name = 'История решения задачи'
        verbose_name_plural = 'История решений задач'

    def __str__(self):
        """Отображение как строка"""
        return str(self.job_id)
