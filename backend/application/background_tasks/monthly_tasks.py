from celery import shared_task
from flask import render_template
from datetime import datetime
from application.models import Sponsors, Campaign, AdRequests
from main import create_app
from utils.email_utils import send_email

app = create_app()

@shared_task
def send_monthly_report():
    """
    Task to send monthly reports to all sponsors.
    """
    with app.app_context():
        sponsors = Sponsors.query.all()
        for sponsor in sponsors:
            campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
            report_data = []

            for campaign in campaigns:
                ads_pending = AdRequests.query.filter_by(campaign_id=campaign.id).count()
                budget_used = campaign.budget_used
                budget_remaining = campaign.budget - budget_used
                report_data.append({
                    'name': campaign.name,
                    'ads_pending': ads_pending,
                    'budget_used': budget_used,
                    'budget': campaign.budget,
                    'budget_remaining': budget_remaining,
                })

            # Define the context for the email template
            html = render_template(
                'monthly_report.html',
                sponsor_name=sponsor.name,
                campaigns=report_data,
                month=datetime.now().strftime('%B'),
                remaining_budget=sum(c['budget_remaining'] for c in report_data)
            )

            # Send the email
            subject = f"Monthly Activity Report - {datetime.now().strftime('%B %Y')}"
            recipient_email = sponsor.email
            send_email(to=recipient_email, subject=subject, content_body=html)
