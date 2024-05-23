import re
import logging
import asyncio
from datetime import datetime, timedelta
from simplegmail import Gmail
from aiogram import Bot
from aiogram.utils.i18n import I18n


logger = logging.getLogger(__name__)


async def mail_parser(bot: Bot):
    gmail = Gmail(noauth_local_webserver=True)

    current_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    query = f'from:nsk@galileopark.ru after:{current_date}'

    messages = gmail.get_messages(query=query)

    quantity_pattern = re.compile(r'Количество\s+(\d+)')
    paid_pattern = re.compile(r'Оплачено\s+([\d\s]+)')
    lab_total_pattern = re.compile(r'Лаборатория всего \(%\)\s+([\d,]+)')
    souvenirs_pattern = re.compile(r'Сувениры\s+([\d,]+)')

    for message in messages:
        print(f'Subject: {message.subject}')

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

        await bot.send_message(chat_id=-1002235736510, text=result)
        print(f'Parsed data: {result}\n')


bot = Bot('', parse_mode='HTML')
asyncio.run(mail_parser(bot=bot))
