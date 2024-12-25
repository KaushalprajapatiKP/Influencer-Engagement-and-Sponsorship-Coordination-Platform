import csv
import os
from celery import shared_task
from application.models import Campaign 
from utils.email_utils import send_email  
from main import create_app  

app = create_app()

@shared_task
def export_campaigns(sponsor_id, sponsor_email):
    with app.app_context():
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
        csv_file_path = f'exports/campaigns_{sponsor_id}.csv'
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
        if not campaigns:
            subject = "No Campaigns to Export"
            content_body = "Dear Sponsor, there are currently no campaigns to export."
            send_email(to=sponsor_email, subject=subject, content_body=content_body)
            return None

        try:
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Campaign ID', 'Campaign Name', 'Description', 'Start Date', 
                                'End Date', 'Budget', 'Visibility', 'Goals', 'Status', 
                                'Created At', 'Updated At'])
                
                for campaign in campaigns:
                    writer.writerow([
                        campaign.id,
                        campaign.name,
                        campaign.description,
                        campaign.start_date,
                        campaign.end_date,
                        campaign.budget,
                        campaign.budget_used,  
                        campaign.visibility,
                        campaign.goals,
                        campaign.flagged,
                    ])

                        
            subject = "Your Campaign Export is Ready"
            content_body = f"Dear Sponsor, your campaign export is ready. You can download it here: {csv_file_path}"
            send_email(to=sponsor_email, subject=subject, content_body=content_body)
        
        except Exception as e:
            return e
        
        return csv_file_path 
