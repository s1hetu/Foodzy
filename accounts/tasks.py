# todo/tasks.py

from celery import shared_task
from django.core.mail import EmailMessage
import logging

logger = logging.getLogger('info_log')


@shared_task()
def send_mail_task(subject, html_content, to):
    msg = EmailMessage(subject, html_content, to=[to])
    if msg.send():
        logger.info(f'Mail sending successful for email {to} and subject is {subject}')
    else:
        logger.error(f'Mail sending failed for email {to} and subject is {subject}')
