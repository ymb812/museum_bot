import imaplib
import email
from email.header import decode_header
import re


# Логин и пароль от почтового ящика
username = ''  # TODO: TO .ENV
password = ''

# Подключение к серверу
mail = imaplib.IMAP4_SSL('imap.mail.ru', 993)
mail.login(username, password)

# Выбор почтового ящика
mail.select('inbox')

# Поиск писем от определенного отправителя
status, messages = mail.search(None, 'FROM', '"nsk@galileopark.ru"')

# Разбиваем результат на список почтовых идентификаторов
mail_ids = messages[0].split()

# Объявление шаблонов для извлечения данных из письма
quantity_pattern = re.compile(r'Количество\s+(\d+)')
paid_pattern = re.compile(r'Оплачено\s+([\d\s]+)')
lab_total_pattern = re.compile(r'Лаборатория всего \(%\)\s+([\d,]+)')
souvenirs_pattern = re.compile(r'Сувениры\s+([\d,]+)')

for mail_id in mail_ids:
    status, msg_data = mail.fetch(mail_id, '(RFC822)')
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            # Парсим содержимое письма с помощью email-пакета
            msg = email.message_from_bytes(response_part[1])
            subject, encoding = decode_header(msg['Subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding)

            from_ = msg.get('From')
            print('Subject:', subject)
            print('From:', from_)

            # Считываем всё тело письма
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                content_type = msg.get_content_type()
                if content_type == 'text/plain':
                    body = msg.get_payload(decode=True).decode()

            # Парсим текст письма с помощью регулярных выражений
            quantity = quantity_pattern.search(body).group(1)
            paid = paid_pattern.search(body).group(1).replace(' ', '')
            lab_total = lab_total_pattern.search(body).group(1).replace(',', '.')
            souvenirs = souvenirs_pattern.search(body).group(1).replace(',', '.')

            result = f'{quantity} {paid} {lab_total} {souvenirs}'
            print('Parsed data:', result)

# Разлогиниваемся и закрываем соединение
mail.logout()
