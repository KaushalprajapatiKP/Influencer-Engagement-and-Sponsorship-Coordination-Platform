from celery import shared_task
from datetime import datetime, timedelta
from ..models import Influencers, User, AdRequests  # Update with your actual import path
from sqlalchemy import or_, and_
import requests  # For Google Chat Webhook
from main import create_app

# Webhook URL for Google Chat 
GOOGLE_CHAT_WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAAA2VAj-ss/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=kM7i05ioIKz1NGAougSwsulV8fQ4TS4JxDpYT2BoJJ4"

app = create_app()

@shared_task(name='send_daily_reminder.send_daily_reminders')
def send_daily_reminders():
    """Send daily reminders to inactive influencers via Google Chat Webhook or SMS."""
    inactivity_period = timedelta(days=7)
    inactive_since = datetime.utcnow() - inactivity_period
    with app.app_context():
        inactive_influencers = (
            Influencers.query
            .join(User)
            .outerjoin(AdRequests, AdRequests.influencer_id == Influencers.id)
            .filter(
                or_(
                    User.last_login_at <= inactive_since,
                    and_(
                        AdRequests.status == "Influencer-Pending",
                        AdRequests.influencer_id == Influencers.id
                    )
                )
            )
            .group_by(Influencers.id)
            .all()
        )
    for influencer in inactive_influencers:
        message = (
            f"Hello {influencer.name},\n\n"
            "It looks like you haven't logged in recently or you have pending ad requests.\n"
            "Please log in to your account to review your requests and explore new campaigns.\n"
            "You can login from here:\n"
            "http://localhost:8081/login\n\n\n"
            "Best regards,\nKaushal,\nIESCP team"
        )
        
        if GOOGLE_CHAT_WEBHOOK_URL:
            send_google_chat_notification(message)
        else:
            print(f"Could not send message to {influencer.name} (no Webhook URL set)")

def send_google_chat_notification(message):
    """Send a notification message via Google Chat Webhook."""
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    data = {"text": message}

    try:
        response = requests.post(GOOGLE_CHAT_WEBHOOK_URL, headers=headers, json=data)
        response.raise_for_status()
        print("Notification sent successfully to Google Chat.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification to Google Chat: {e}")
