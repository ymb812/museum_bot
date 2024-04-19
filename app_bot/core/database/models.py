import logging
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
    is_reports_receiver = fields.BooleanField(default=False)
    fio = fields.CharField(max_length=64, null=True)
    phone = fields.CharField(max_length=64, null=True)
    email = fields.CharField(max_length=64, null=True)
    link = fields.CharField(max_length=64, unique=True, null=True)

    user_id = fields.BigIntField(null=True, unique=True)
    username = fields.CharField(max_length=32, index=True, null=True)
    status = fields.CharField(max_length=32, null=True)  # admin
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


    @classmethod
    async def update_admin_data(cls, user_id: int, username: str, status: str):
        user = await cls.get_or_none(user_id=user_id)
        if user is None:
            await cls.create(
                user_id=user_id,
                username=username,
                status=status
            )
        else:
            user.status = status
            await user.save()


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
    description = fields.CharField(max_length=1024, null=True)
    exhibit = fields.ForeignKeyField(model_name='models.Exhibit', to_field='id')
    museum = fields.ForeignKeyField(model_name='models.Museum', to_field='id')
    session = fields.ForeignKeyField(model_name='models.ReportSession', to_field='id', null=True)
    creator = fields.ForeignKeyField(model_name='models.User', to_field='user_id')
    created_at = fields.DatetimeField(auto_now_add=True)


class ReportSession(Model):
    class Meta:
        table = 'report_sessions'
        ordering = ['created_at']

    id = fields.IntField(pk=True, index=True)
    creator = fields.ForeignKeyField(model_name='models.User', to_field='user_id')
    created_at = fields.DatetimeField(auto_now_add=True)


class Dispatcher(Model):
    class Meta:
        table = 'mailings'
        ordering = ['id']

    id = fields.BigIntField(pk=True)
    post = fields.ForeignKeyField('models.Post', to_field='id')
    museum = fields.ForeignKeyField(model_name='models.Museum', to_field='id', null=True)
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
