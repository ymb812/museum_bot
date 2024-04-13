import string
import random
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from admin_panel_for_bot.settings import settings


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class User(models.Model):
    class Meta:
        db_table = 'users'
        ordering = ['created_at']
        verbose_name = 'Сотрудники'
        verbose_name_plural = verbose_name

    id = models.AutoField(primary_key=True, db_index=True)
    is_reports_receiver = models.BooleanField(default=False, verbose_name='Получает отчет после осмотра?')
    museum = models.ForeignKey('Museum', to_field='id', null=True, on_delete=models.SET_NULL)
    fio = models.CharField(max_length=64, null=True)
    phone = models.CharField(max_length=64, null=True, blank=True)
    email = models.CharField(max_length=64, null=True, blank=True)
    link = models.CharField(max_length=64, unique=True, null=True, blank=True)

    user_id = models.BigIntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=32, db_index=True, blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.fio}'

    def save(self, *args, **kwargs):
        self.link = settings.bot_link + generate_random_string(5)

        return super(User, self).save(*args, **kwargs)


class Museum(models.Model):
    class Meta:
        db_table = 'museums'
        ordering = ['id']
        verbose_name = 'Музеи'
        verbose_name_plural = verbose_name

    id = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Exhibit(models.Model):
    class Meta:
        db_table = 'exhibits'
        ordering = ['id']
        verbose_name = 'Экспонаты'
        verbose_name_plural = verbose_name

    id = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=64)
    media_content = models.CharField(max_length=256, null=True, blank=True)
    museum = models.ForeignKey('Museum', to_field='id', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Report(models.Model):
    class Meta:
        db_table = 'reports'
        ordering = ['id']
        verbose_name = 'Отчеты'
        verbose_name_plural = verbose_name

    class StatusType(models.TextChoices):
        work = 'Работает', 'Работает'
        broken = 'Сломан', 'Сломан'
        admin_request = 'Требует внимания админа', 'Требует внимания админа'
        engineer_request = 'Требует внимания техника', 'Требует внимания техника'

    id = models.AutoField(primary_key=True, db_index=True)
    status = models.CharField(max_length=32, choices=StatusType)
    description = models.CharField(max_length=1024, null=True)
    exhibit = models.ForeignKey('Exhibit', to_field='id', on_delete=models.CASCADE)
    museum = models.ForeignKey('Museum', to_field='id', on_delete=models.CASCADE)
    creator = models.ForeignKey('User', to_field='user_id', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

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
    museum = models.ForeignKey('Museum', to_field='id', null=True, on_delete=models.SET_NULL, blank=True)
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
