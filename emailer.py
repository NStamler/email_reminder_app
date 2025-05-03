import smtplib
import os
from email.mime.text import MIMEText
from flask import url_for

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = os.getenv("EMAIL_ADDRESS", "you@example.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Edit this to match your Render app URL
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

def send_email(recipient, subject, body):
    msg = MIMEText(body, 'plain')
    msg['Subject'] = subject
    msg['From'] = f"Calendar Reminder Bot <{FROM_EMAIL}>"
    msg['To'] = recipient

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(FROM_EMAIL, EMAIL_PASSWORD)
            server.sendmail(FROM_EMAIL, recipient, msg.as_string())
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")

def send_confirmation_email(email, token):
    link = f"{BASE_URL}/edit/{token}"
    subject = "Confirm your event reminder signup"
    body = f"Thanks for signing up!\n\nYou can edit your reminder preferences here:\n{link}\n\nTo unsubscribe at any time:\n{BASE_URL}/unsubscribe/{token}"
    send_email(email, subject, body)

def send_edit_link(email, token):
    link = f"{BASE_URL}/edit/{token}"
    subject = "Edit your event reminder preferences"
    body = f"You can edit your preferences here:\n{link}\n\nTo unsubscribe:\n{BASE_URL}/unsubscribe/{token}"
    send_email(email, subject, body)
