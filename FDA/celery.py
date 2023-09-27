# FDA/celery.py
import calendar
import datetime
import os

from celery import Celery
from celery.schedules import crontab

from dotenv import load_dotenv

# loads environment variable from .env file
load_dotenv()


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FDA.settings")
app = Celery("FDA")
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')

app.config_from_object("django.conf:settings", namespace="CELERY")


def get_last_date():
    today = datetime.datetime.now()
    year = today.year
    month = today.month
    last_date = calendar.monthrange(year, month)[1]
    return str(last_date)


app.conf.beat_schedule = {
    # Schedulers
    'send_payouts_at_month_end': {
        'task': 'orders.tasks.schedule_payout',
        'schedule': crontab(0, 0, day_of_month='5'),  # Execute on the (minutes(0-59), hour(0-23), day_of_month(0-31)) fifth day of every month.
    }
}

app.autodiscover_tasks()
