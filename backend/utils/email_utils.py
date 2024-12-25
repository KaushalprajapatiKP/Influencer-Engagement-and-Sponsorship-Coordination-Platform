from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# SMTP Configuration
SMTP_HOST = 'localhost'
SMTP_PORT = 1025
SENDER_EMAIL = 'Kaushal@study.iitm.ac.in'

def send_email(to, subject, content_body):
    """
    Function to send an email with HTML content.
    :param to: Recipient email address
    :param subject: Subject of the email
    :param content_body: HTML content of the email
    """
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(content_body, 'html')) 

    try:
        with SMTP(host=SMTP_HOST, port=SMTP_PORT) as client:
            client.send_message(msg)
            print("Email sent successfully to", to)
    except Exception as e:
        print(f"Failed to send email: {e}")
