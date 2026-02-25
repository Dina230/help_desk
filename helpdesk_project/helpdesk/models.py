from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinLengthValidator
import os


def problem_file_path(instance, filename):
    return f'problems/{instance.id}/{filename}'


def solution_file_path(instance, filename):
    return f'solutions/{instance.id}/{filename}'


class Direction(models.Model):
    DIRECTIONS = [
        ('OS', 'Операционная система'),
        ('ZUP', '1с ЗиУП'),
        ('PU', '1с ПУ'),
        ('BU', '1с БУ'),
        ('TEL', 'Телефония'),
        ('VIDEO_PKS', 'Видеонаблюдение на ПКС'),
        ('VIDEO_PC', 'Видеонаблюдение общие проблемы с ПК'),
    ]

    name = models.CharField(max_length=20, choices=DIRECTIONS, unique=True)
    display_name = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = dict(self.DIRECTIONS)[self.name]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['name']


class Problem(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(
        validators=[MaxLengthValidator(300)],
        verbose_name="Описание проблемы"
    )
    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE,
        related_name='problems',
        verbose_name="Направление"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='problems',
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.author.username}"

    class Meta:
        ordering = ['-created_at']


class ProblemFile(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(upload_to=problem_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)


class Solution(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='solutions',
        verbose_name="Проблема"
    )
    description = models.TextField(
        validators=[MaxLengthValidator(800)],
        verbose_name="Описание решения"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solutions',
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False, verbose_name="Принятое решение")

    def __str__(self):
        return f"Решение к {self.problem.title} от {self.author.username}"

    class Meta:
        ordering = ['-is_accepted', '-created_at']


class SolutionFile(models.Model):
    solution = models.ForeignKey(
        Solution,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(upload_to=solution_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)