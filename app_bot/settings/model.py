from pydantic import BaseModel, SecretStr, fields
from pydantic_settings import SettingsConfigDict


class BotSettings(BaseModel):
    bot_token: SecretStr = fields.Field(max_length=100, alias='TELEGRAM_BOT_TOKEN')
    bot_link: str = fields.Field(max_length=100, alias='BOT_BASE_LINK')
    admin_password: SecretStr = fields.Field(max_length=100, alias='ADMIN_PASSWORD')
    admin_chat_link: str = fields.Field(alias='ADMIN_CHAT_LINK')
    required_channel_id: str = fields.Field(alias='REQUIRED_CHANNEL_ID')
    welcome_post_id: int = fields.Field(alias='WELCOME_POST_ID')
    notification_post_id: int = fields.Field(alias='NOTIFICATION_POST_ID')
    registered_post_id: int = fields.Field(alias='REGISTERED_POST_ID')

class Dialogues(BaseModel):
    categories_per_page_height: int = fields.Field(alias='CATEGORIES_HEIGHT')
    categories_per_page_width: int = fields.Field(alias='CATEGORIES_WIDTH')

class Broadcaster(BaseModel):
    mailing_batch_size: int = fields.Field(alias='MAILING_BATCH_SIZE', default=25)
    broadcaster_sleep: int = fields.Field(alias='BROADCASTER_SLEEP', default=1)
    notification_hours: int = fields.Field(alias='NOTIFICATION_HOURS', default=10)
    notification_minutes: int = fields.Field(alias='NOTIFICATION_MINUTES', default=0)
    nvg_chat_id: str = fields.Field(alias='NVG_CHAT_ID')
    spb_chat_id: str = fields.Field(alias='SPB_CHAT_ID')
    samara_chat_id: str = fields.Field(alias='SAMARA_CHAT_ID')
    nsk_chat_id: str = fields.Field(alias='NSK_CHAT_ID')
    krsk_chat_id: str = fields.Field(alias='KRSK_CHAT_ID')

class AppSettings(BaseModel):
    prod_mode: bool = fields.Field(alias='PROD_MODE', default=False)
    excel_file: str = fields.Field(alias='EXCEL_FILE', default='Users stats.xlsx')
    mail_login: str = fields.Field(max_length=100, alias='MAIL_LOGIN')
    mail_password: str = fields.Field(max_length=100, alias='MAIL_PASSWORD')


class PostgresSettings(BaseModel):
    db_user: str = fields.Field(alias='POSTGRES_USER')
    db_host: str = fields.Field(alias='POSTGRES_HOST')
    db_port: int = fields.Field(alias='POSTGRES_PORT')
    db_pass: SecretStr = fields.Field(alias='POSTGRES_PASSWORD')
    db_name: SecretStr = fields.Field(alias='POSTGRES_DATABASE')


class RedisSettings(BaseModel):
    redis_host: str = fields.Field(alias='REDIS_HOST')
    redis_port: int = fields.Field(alias='REDIS_PORT')
    redis_name: str = fields.Field(alias='REDIS_NAME')


class Settings(
    BotSettings,
    AppSettings,
    PostgresSettings,
    Broadcaster,
    Dialogues,
    RedisSettings
):
    model_config = SettingsConfigDict(extra='ignore')
