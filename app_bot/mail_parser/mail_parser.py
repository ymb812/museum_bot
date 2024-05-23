import re
import logging
import pytz
from datetime import datetime, timedelta
from simplegmail import Gmail
from aiogram import Bot
from settings import settings


logger = logging.getLogger(__name__)


async def mail_parser(bot: Bot, cities: str, hour: int):
    gmail = Gmail(noauth_local_webserver=True)

    yesterday = datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=1)
    start_date = yesterday.replace(hour=hour, minute=0, second=0, microsecond=0)  # to parse mails after last checking

    query = f'from:nsk@galileopark.ru after:{yesterday.strftime("%Y-%m-%d")}'
    messages = gmail.get_messages(query=query)

    quantity_pattern = re.compile(r'Количество\s+(\d+)')
    paid_pattern = re.compile(r'Оплачено\s+([\d\s]+)')
    lab_total_pattern = re.compile(r'Лаборатория всего \(%\)\s+([\d,]+)')
    souvenirs_pattern = re.compile(r'Сувениры\s+([\d,]+)')

    for message in messages:
        # check hours
        message_date = datetime.fromisoformat(message.date)
        if message_date < start_date:
            continue

        try:
            body = message.plain
            quantity_match = quantity_pattern.search(body)
            paid_match = paid_pattern.search(body)
            lab_total_match = lab_total_pattern.search(body)
            souvenirs_match = souvenirs_pattern.search(body)

            quantity = quantity_match.group(1) if quantity_match else 'N/A'
            paid = re.sub(r'\s', '', paid_match.group(1)) if paid_match else 'N/A'
            lab_total = lab_total_match.group(1).replace(',', '.') if lab_total_match else 'N/A'
            souvenirs = souvenirs_match.group(1).replace(',', '.') if souvenirs_match else 'N/A'

            result = f'{round(float(paid) / 1000, 1)};{quantity};{round(float(souvenirs))};{round(float(lab_total))}'

            # send by cities
            if 'Нижний Новгород' in message.subject and 'nvg_spb' in cities:
                await bot.send_message(chat_id=settings.nvg_chat_id, text=result)
                logger.info(f'msg was sent to the {cities}')

            if 'Санкт-Петербург' in message.subject and 'nvg_spb' in cities:
                await bot.send_message(chat_id=settings.spb_chat_id, text=result)
                logger.info(f'msg was sent to the {cities}')

            if 'Самара' in message.subject and 'samara' in cities:
                await bot.send_message(chat_id=settings.samara_chat_id, text=result)
                logger.info(f'msg was sent to the {cities}')

            if 'Новосибирск' in message.subject and 'nsk_krsk' in cities:
                await bot.send_message(chat_id=settings.nsk_chat_id, text=result)
                logger.info(f'msg was sent to the {cities}')

            if 'Красноярск' in message.subject and 'nsk_krsk' in cities:
                await bot.send_message(chat_id=settings.krsk_chat_id, text=result)
                logger.info(f'msg was sent to the {cities}')

            logger.info(f'{message.date} {message.subject} {result}')

        except Exception as e:
            logger.error(f'Error to send message: {message.plain}\n{message.date}', exc_info=e)
