import logging
from datetime import datetime
from tortoise import fields
from tortoise.models import Model
from enum import Enum


logger = logging.getLogger(__name__)


class User(Model):
    class Meta:
        table = 'users'
        ordering = ['created_at']

    id = fields.IntField(pk=True, index=True)
    museum = fields.ForeignKeyField(model_name='models.Museum', to_field='id', null=True)
    fio = fields.CharField(max_length=64, null=True)
    phone = fields.CharField(max_length=64, null=True)
    email = fields.CharField(max_length=64, null=True)
    link = fields.CharField(max_length=64, unique=True)

    user_id = fields.BigIntField(null=True)
    username = fields.CharField(max_length=32, index=True, null=True)
    status = fields.CharField(max_length=32, null=True)  # admin/worker
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @classmethod
    async def update_data(cls, user_id: int, first_name: str, last_name: str, username: str, language_code: str,
                          is_premium: bool, link: str = None):
        if link:
            user = await cls.filter(link=link).first()
        else:
            user = await cls.filter(user_id=user_id).first()
        if user is None:
            await cls.create(
                user_id=user_id,
                username=username,
                is_premium=is_premium,
            )
        else:
            if link:
                await cls.filter(link=link).update(
                    user_id=user_id,
                    username=username,
                    updated_at=datetime.now()
                )

    @classmethod
    async def set_status(cls, user_id: int, status: str | None):
        await cls.filter(user_id=user_id).update(status=status)


class Museum(Model):
    class Meta:
        table = 'museums'
        ordering = ['id']

    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=64)


class Exhibit(Model):
    class Meta:
        table = 'exhibits'
        ordering = ['id']

    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=64)
    media_content = fields.CharField(max_length=256, null=True)
    museum = fields.ForeignKeyField(model_name='models.Museum', to_field='id', null=True)


class Report(Model):
    class Meta:
        table = 'reports'
        ordering = ['id']

    class StatusType(Enum):
        work = 'Работает'
        broken = 'Сломан'
        admin_request = 'Требует внимания админа'
        engineer_request = 'Требует внимания техника'

    id = fields.IntField(pk=True, index=True)
    status = fields.CharEnumField(enum_type=StatusType, default=StatusType.work, max_length=64)
    description = fields.CharField(max_length=1024)
    exhibit = fields.ForeignKeyField(model_name='models.Exhibit', to_field='id', null=True)
    museum = fields.ForeignKeyField(model_name='models.Museum', to_field='id', null=True)
    created_at = fields.DatetimeField(auto_now_add=True)


class Dispatcher(Model):
    class Meta:
        table = 'mailings'
        ordering = ['id']

    id = fields.BigIntField(pk=True)
    post = fields.ForeignKeyField('models.Post', to_field='id')
    send_at = fields.DatetimeField()


class Post(Model):
    class Meta:
        table = 'static_content'

    id = fields.BigIntField(pk=True)
    text = fields.TextField(null=True)
    photo_file_id = fields.CharField(max_length=256, null=True)
    video_file_id = fields.CharField(max_length=256, null=True)
    video_note_id = fields.CharField(max_length=256, null=True)
    document_file_id = fields.CharField(max_length=256, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
