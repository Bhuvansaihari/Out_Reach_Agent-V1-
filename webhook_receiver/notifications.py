import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client as TwilioClient
from datetime import datetime

def send_email(candidate_email, subject, html_content, from_email=None):
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = from_email or os.getenv("SENDGRID_FROM_EMAIL")
    if not api_key or not from_email:
        raise Exception("Missing SendGrid config")
    sg = SendGridAPIClient(api_key)
    message = Mail(
        from_email=from_email,
        to_emails=candidate_email,
        subject=subject,
        html_content=html_content
    )
    response = sg.send(message)
    return response.status_code

def send_sms(candidate_mobile, message_body):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE_NUMBER")
    if not account_sid or not auth_token or not from_phone:
        raise Exception("Missing Twilio config")
    client = TwilioClient(account_sid, auth_token)
    message = client.messages.create(
        body=message_body,
        from_=from_phone,
        to=candidate_mobile
    )
    return message.sid