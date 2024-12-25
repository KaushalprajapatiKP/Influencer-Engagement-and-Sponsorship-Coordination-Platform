from celery import Celery
from config import DevelopmentConfig
from celery.schedules import crontab

# Initialization of celery with redis connection
celery = Celery("backend", broker=DevelopmentConfig.broker_url, backend=DevelopmentConfig.result_backend)
celery.config_from_object(DevelopmentConfig)

from application.background_tasks.daily_tasks import send_daily_reminders
from application.background_tasks.monthly_tasks import send_monthly_report
from application.background_tasks.export_tasks import export_campaigns


# Set up the periodic task schedule
celery.conf.beat_schedule = {
    "send_daily_reminders": {
        "task": "application.background_tasks.daily_tasks.send_daily_reminders",
        "schedule": crontab(hour=17, minute=0),  # Runs daily at 5 PM UTC
        "options": {"expires": 3600},  
    },
    "send_monthly_report": {
        "task": "application.background_tasks.monthly_tasks.send_monthly_report",
        "schedule": crontab(0, 0, day_of_month=1),  # Runs at midnight on the 1st day of every month
    },
}

# This ensures the Celery worker recognizes the task
celery.autodiscover_tasks(["application.background_tasks"])



# Manually Calling all the background tasks
send_daily_reminders.delay()  
send_monthly_report.apply_async()  
export_campaigns.delay(2,"kaushal@gmail.com")