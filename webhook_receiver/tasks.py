"""
Celery tasks for sending email and SMS notifications
"""
import os
from celery import Task
from celery_app import celery_app
from webhook_receiver.database import (
    get_application_details, mark_email_sent, mark_sms_sent
)
from webhook_receiver.utils import (
    format_phone_number, validate_phone_number, extract_plain_description
)
from webhook_receiver.email_template import render_email_template, get_email_subject
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client as TwilioClient
import re
import html


class CallbackTask(Task):
    """Base task with error callbacks"""
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(f"❌ Task {task_id} failed: {exc}")
        # Could send alert notification here


@celery_app.task(
    bind=True,
    base=CallbackTask,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=900,
    retry_jitter=True
)
def send_notification_task(self, cand_id: int, requirement_id: str):
    """
    Main task to process notifications for a job application
    
    Args:
        cand_id: Candidate ID
        requirement_id: Requirement ID
    """
    try:
        print(f"🔍 Processing notification for cand_id: {cand_id}, requirement_id: {requirement_id}")
        
        # Get application details
        app_data = get_application_details(cand_id, requirement_id)
        if not app_data:
            print("⏸️ Application not found or already sent. Skipping.")
            return {"status": "skipped", "reason": "already_sent"}

        candidate = app_data['candidate']
        requirement = app_data['requirement']
        application_id = app_data['application_id']
        application_status = app_data['application_status']
        email_sent = app_data['email_sent']
        sms_sent = app_data['sms_sent']
        notify_email = candidate.get("notify_email", True)
        notify_sms = candidate.get("notify_sms", False)

        # Extract and clean description
        raw_description = requirement.get('requirement_description', '')
        plain_desc = extract_plain_description(raw_description)
        clean_description = re.sub(r'<[^>]+>', '', plain_desc)
        clean_description = html.unescape(clean_description)
        if len(clean_description) > 250:
            clean_description = clean_description[:250].strip() + '...'

        first_name = candidate['candidate_first_name']
        match_score_int = int(requirement['similarity_score'] * 100)
        job_type = "Contract"
        if requirement.get('requirement_duration'):
            job_type = f"Contract ({requirement['requirement_duration']})"

        results = {"email": None, "sms": None}

        # Send Email
        if notify_email and not email_sent:
            try:
                email_result = send_email_task.delay(
                    application_id=application_id,
                    candidate_email=candidate['candidate_email'],
                    first_name=first_name,
                    job_title=requirement['requirement_title'],
                    company_name=requirement.get('client_name', 'N/A'),
                    location=requirement.get('location', 'Remote'),
                    job_type=job_type,
                    match_score=str(match_score_int),
                    clean_description=clean_description,
                    application_status=application_status.upper()
                )
                results["email"] = "queued"
                print("✅ Email task queued")
            except Exception as email_error:
                print(f"❌ Email task failed: {email_error}")
                results["email"] = f"failed: {email_error}"
        else:
            print("⏭️ Email not sent (preference false or already sent)")
            results["email"] = "skipped"

        # Send SMS
        if notify_sms and not sms_sent:
            candidate_mobile = (
                candidate.get('candidate_mobile') or 
                candidate.get('candidate_work') or 
                candidate.get('candidate_home') or 
                ''
            )
            formatted_phone = format_phone_number(candidate_mobile)
            if candidate_mobile and validate_phone_number(formatted_phone):
                try:
                    sms_text = (
                        f"Hi {first_name or 'Candidate'}! "
                        f"Job Matched: {requirement['requirement_title']} "
                        f"({match_score_int}% fit). "
                        "Auto-applied for you. Recruiter will contact soon!"
                    )[:160]
                    sms_result = send_sms_task.delay(
                        application_id=application_id,
                        phone_number=formatted_phone,
                        message=sms_text
                    )
                    results["sms"] = "queued"
                    print("✅ SMS task queued")
                except Exception as sms_error:
                    print(f"❌ SMS task failed: {sms_error}")
                    results["sms"] = f"failed: {sms_error}"
            else:
                print("⚠️ No valid phone for SMS")
                results["sms"] = "invalid_phone"
        else:
            print("⏭️ SMS not sent (preference false or already sent)")
            results["sms"] = "skipped"

        return {
            "status": "completed",
            "cand_id": cand_id,
            "requirement_id": requirement_id,
            "results": results
        }

    except Exception as e:
        print(f"❌ Error in notification task: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=CallbackTask,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_email_task(self, application_id, candidate_email, first_name, job_title, 
                    company_name, location, job_type, match_score, clean_description, 
                    application_status):
    """
    Send email notification via SendGrid
    """
    try:
        # Render email template
        rendered_email_html = render_email_template(
            candidate_name=first_name,
            job_title=job_title,
            company_name=company_name,
            location=location,
            job_type=job_type,
            match_score=match_score,
            short_description=clean_description,
            application_status=application_status
        )
        
        email_subject = get_email_subject(
            job_title=job_title,
            company_name=company_name,
            match_score=match_score
        )

        # Send via SendGrid
        api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("SENDGRID_FROM_EMAIL")
        sg = SendGridAPIClient(api_key)
        message = Mail(
            from_email=from_email,
            to_emails=candidate_email,
            subject=email_subject,
            html_content=rendered_email_html
        )
        response = sg.send(message)
        
        # Mark as sent in database
        mark_email_sent(application_id)
        print(f"✅ Email sent successfully to {candidate_email}")
        
        return {
            "status": "success",
            "status_code": response.status_code,
            "application_id": application_id
        }
        
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        # Don't retry on auth errors
        if "401" in str(e) or "Unauthorized" in str(e):
            print("⚠️ Authentication error - not retrying")
            return {"status": "auth_error", "error": str(e)}
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=CallbackTask,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_sms_task(self, application_id, phone_number, message):
    """
    Send SMS notification via Twilio
    """
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_phone = os.getenv("TWILIO_PHONE_NUMBER")
        
        client = TwilioClient(account_sid, auth_token)
        twilio_message = client.messages.create(
            body=message,
            from_=from_phone,
            to=phone_number
        )
        
        # Mark as sent in database
        mark_sms_sent(application_id)
        print(f"✅ SMS sent successfully to {phone_number}")
        
        return {
            "status": "success",
            "sid": twilio_message.sid,
            "application_id": application_id
        }
        
    except Exception as e:
        print(f"❌ SMS send failed: {e}")
        raise self.retry(exc=e)
