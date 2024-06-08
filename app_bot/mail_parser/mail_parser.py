import re
import logging
import pytz
import imaplib
import email
from datetime import datetime, timedelta
from email.policy import default
from aiogram import Bot
from core.database.models import CitiesForParser
from settings import settings

logger = logging.getLogger(__name__)


async def mail_parser(bot: Bot, city: CitiesForParser):
    imap_host = 'imap.gmail.com'
    username = settings.mail_login
    password = settings.mail_password

    try:
        # Connect to the server
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(username, password)
        mail.select('inbox')

        yesterday = datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=1)
        start_date = yesterday.replace(hour=city.hour, minute=city.minute, second=0, microsecond=0)
        start_date_str = start_date.strftime('%d-%b-%Y')

        query = f'(FROM "nsk@galileopark.ru" SINCE {start_date_str})'
        result, data = mail.search(None, query)

        if result != 'OK':
            logger.error('No emails found!')
            return

        mail_ids = data[0].split()

        quantity_pattern = re.compile(r'Количество\s+(\d+)')
        paid_pattern = re.compile(r'Оплачено\s+([\d\s]+)')
        lab_total_pattern = re.compile(r'Лаборатория всего \(%\)\s+([\d,]+)')
        souvenirs_pattern = re.compile(r'Сувениры\s+([\d,]+)')

        for mail_id in mail_ids:
            result, message_data = mail.fetch(mail_id, '(RFC822)')
            if result != 'OK':
                logger.error(f'Failed to fetch email with ID {mail_id}')
                continue

            for response_part in message_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1], policy=default)
                    msg_date = msg['Date']
                    # Extract and parse the message date
                    message_date = datetime.strptime(msg_date, '%a, %d %b %Y %H:%M:%S %z')
                    message_date = message_date.astimezone(pytz.timezone('Europe/Moscow'))

                    if message_date < start_date:
                        continue

                    try:
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == 'text/plain':
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()

                        quantity_match = quantity_pattern.search(body)
                        paid_match = paid_pattern.search(body)
                        lab_total_match = lab_total_pattern.search(body)
                        souvenirs_match = souvenirs_pattern.search(body)

                        quantity = quantity_match.group(1) if quantity_match else 'N/A'
                        paid = re.sub(r'\s', '', paid_match.group(1)) if paid_match else 'N/A'
                        lab_total = lab_total_match.group(1).replace(',', '.') if lab_total_match else 'N/A'
                        souvenirs = souvenirs_match.group(1).replace(',', '.') if souvenirs_match else 'N/A'

                        # Ensure conversion to float before division
                        paid = round(float(paid) / 1000, 1) if paid != 'N/A' else 'N/A'
                        lab_total = round(float(lab_total)) if lab_total != 'N/A' else 'N/A'
                        souvenirs = round(float(souvenirs)) if souvenirs != 'N/A' else 'N/A'

                        result = f'{paid};{quantity};{souvenirs};{lab_total}'


                        # work with city: CitiesForParser
                        subject = msg['Subject']
                        if city.name in subject:
                            await bot.send_message(chat_id=city.channel_id, text=result)
                            logger.info(f'Message was sent to {city.name} and chat_id={city.channel_id}')
                            logger.info(f'{message_date} > {start_date}')

                    except Exception as e:
                        logger.error(f'Error parsing email {mail_id}: {e}', exc_info=True)

    except Exception as e:
        logger.error(f'Error connecting to the email server: {e}', exc_info=True)
    finally:
        mail.logout()
