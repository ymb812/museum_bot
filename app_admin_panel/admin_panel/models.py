from django.db import models
from enum import Enum


class User(models.Model):
    class Meta:
        db_table = 'users'
        ordering = ['created_at']
        verbose_name = 'Пользователи'
        verbose_name_plural = verbose_name

    user_id = models.BigIntegerField(primary_key=True, db_index=True)
    username = models.CharField(max_length=32, db_index=True, blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    language_code = models.CharField(max_length=2, blank=True, null=True)
    is_premium = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name


class Category(models.Model):
    class Meta:
        db_table = 'categories'
        ordering = ['id']
        verbose_name = 'Категории фильтрации'
        verbose_name_plural = verbose_name

    class ContentType(models.TextChoices):
        budget = 'budget', 'budget'
        commercial = 'commercial', 'commercial'

    id = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=32)
    content_type = models.CharField(max_length=32, choices=ContentType, default=ContentType.commercial)

    def __str__(self):
        return self.name


class Estate(models.Model):
    class Meta:
        db_table = 'estates'
        ordering = ['id']
        verbose_name = 'Объекты недвижимости'
        verbose_name_plural = verbose_name

    id = models.IntegerField(primary_key=True, db_index=True)
    description = models.CharField(max_length=1024)
    media_content = models.CharField(max_length=256, null=True, blank=True)
    presentation = models.CharField(max_length=256, null=True, blank=True)
    parent_category = models.ForeignKey('Category', to_field='id', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.id}'


class Dispatcher(models.Model):
    class Meta:
        db_table = 'mailings'
        ordering = ['id']
        verbose_name = 'Рассылки'
        verbose_name_plural = verbose_name

    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey('Post', to_field='id', on_delete=models.CASCADE)
    send_at = models.DateTimeField()

    def __str__(self):
        return f'{self.id}'


class Post(models.Model):
    class Meta:
        db_table = 'static_content'
        ordering = ['id']
        verbose_name = 'Контент для рассылок'
        verbose_name_plural = verbose_name

    id = models.BigIntegerField(primary_key=True)
    text = models.TextField(blank=True, null=True)
    photo_file_id = models.CharField(max_length=256, blank=True, null=True)
    video_file_id = models.CharField(max_length=256, blank=True, null=True)
    video_note_id = models.CharField(max_length=256, blank=True, null=True)
    document_file_id = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'
