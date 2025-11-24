import asyncio
import html
import re
import os
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime
from webhook_receiver.database import (
    get_application_details, mark_email_sent, mark_sms_sent
)
from webhook_receiver.utils import (
    format_single_requirement, format_phone_number, validate_phone_number, validate_webhook_payload
)
from webhook_receiver.email_template import render_email_template, get_email_subject

# --- Add Email/SMS helpers (use SendGrid/Twilio SDKs directly) ---
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client as TwilioClient

load_dotenv()

app = FastAPI(
    title="Email & SMS Webhook Receiver - Production",
    description="Direct notification FastAPI (no agents) using async concurrency",
    version="6.0"
)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "20"))
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

def send_email(candidate_email, subject, html_content, from_email=None):
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = from_email or os.getenv("SENDGRID_FROM_EMAIL")
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
    client = TwilioClient(account_sid, auth_token)
    message = client.messages.create(
        body=message_body,
        from_=from_phone,
        to=candidate_mobile
    )
    return message.sid

async def process_notifications_for_application(cand_id: int, requirement_id: str):
    async with semaphore:
        try:
            app_data = await asyncio.get_event_loop().run_in_executor(
                None, get_application_details, cand_id, requirement_id)
            if not app_data:
                print("⏸️ Application not found or already sent. Skipping.")
                return

            candidate = app_data['candidate']
            requirement = app_data['requirement']
            application_id = app_data['application_id']
            application_status = app_data['application_status']
            email_sent = app_data['email_sent']
            sms_sent = app_data['sms_sent']
            notify_email = candidate.get("notify_email", True)
            notify_sms = candidate.get("notify_sms", False)

            first_name = candidate['candidate_first_name']
            match_score_int = int(requirement['similarity_score'] * 100)
            job_type = "Contract"
            if requirement.get('requirement_duration'):
                job_type = f"Contract ({requirement['requirement_duration']})"
            description = requirement.get('requirement_description', '')
            clean_description = re.sub(r'<[^>]+>', '', description)
            clean_description = html.unescape(clean_description)
            if len(clean_description) > 250:
                clean_description = clean_description[:250].strip() + '...'

            # EMAIL
            if notify_email and not email_sent:
                rendered_email_html = render_email_template(
                    candidate_name=first_name,
                    job_title=requirement['requirement_title'],
                    company_name=requirement.get('client_name', 'N/A'),
                    location=requirement.get('location', 'Remote'),
                    job_type=job_type,
                    match_score=str(match_score_int),
                    short_description=clean_description,
                    application_status=application_status.upper()
                )
                email_subject = get_email_subject(
                    job_title=requirement['requirement_title'],
                    company_name=requirement.get('client_name', 'N/A'),
                    match_score=str(match_score_int)
                )
                await asyncio.get_event_loop().run_in_executor(
                    None, send_email,
                    candidate['candidate_email'],
                    email_subject,
                    rendered_email_html,
                    os.getenv('SENDGRID_FROM_EMAIL')
                )
                await asyncio.get_event_loop().run_in_executor(
                    None, mark_email_sent, application_id)
                print("✅ Email sent")
            else:
                print("⏭️ Email not sent (preference false or already sent)")

            # SMS
            if notify_sms and not sms_sent:
                candidate_mobile = (
                    candidate.get('candidate_mobile') or 
                    candidate.get('candidate_work') or 
                    candidate.get('candidate_home') or 
                    ''
                )
                formatted_phone = format_phone_number(candidate_mobile)
                if candidate_mobile and validate_phone_number(formatted_phone):
                    sms_text = (
                        f"Hi {first_name or 'Candidate'}! "
                        f"Job Matched: {requirement['requirement_title']} "
                        f"({match_score_int}% fit). "
                        "Auto-applied for you. Recruiter will contact soon!"
                    )[:160]
                    await asyncio.get_event_loop().run_in_executor(
                        None, send_sms, formatted_phone, sms_text
                    )
                    await asyncio.get_event_loop().run_in_executor(
                        None, mark_sms_sent, application_id)
                    print("✅ SMS sent")
                else:
                    print("⚠️ No valid phone for SMS")
            else:
                print("⏭️ SMS not sent (preference false or already sent)")

        except Exception as e:
            print("❌ Error in notification:", e)

class WebhookPayload(BaseModel):
    type: str
    table: str
    record: dict
    schema_name: str = Field(alias="schema")
    old_record: Optional[dict] = None

@app.post("/webhook/job-match")
async def webhook_handler(
    request: Request,
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret")
):
    try:
        payload = await request.json()
        if WEBHOOK_SECRET and x_webhook_secret != WEBHOOK_SECRET:
            print(f"❌ Invalid webhook secret")
            raise HTTPException(status_code=401, detail="Invalid webhook secret")
        print(f"📨 WEBHOOK RECEIVED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if not validate_webhook_payload(payload):
            raise HTTPException(status_code=400, detail="Invalid payload structure")
        if payload['type'] != "INSERT" or payload['table'] != "job_application_tracking":
            return JSONResponse(
                status_code=200,
                content={"status": "ignored"}
            )
        record = payload['record']
        cand_id = record.get('cand_id')
        requirement_id = record.get('requirement_id')
        if not cand_id or not requirement_id:
            raise HTTPException(
                status_code=400, 
                detail="cand_id and requirement_id required"
            )
        asyncio.create_task(
            process_notifications_for_application(cand_id, requirement_id)
        )
        return JSONResponse(
            status_code=202,
            content={
                "status": "accepted",
                "message": f"Notifications queued",
                "cand_id": cand_id,
                "requirement_id": requirement_id,
                "timestamp": datetime.now().isoformat(),
                "concurrency": {"max_concurrent_tasks": MAX_CONCURRENT_TASKS}
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "service": "Email & SMS Webhook Receiver - Production",
        "version": "6.0 (No agents, supports preferences)",
        "capabilities": ["email", "sms", "html_templates", "parallel_processing"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "email-sms-webhook-receiver-production",
        "timestamp": datetime.now().isoformat(),
        "concurrency": {
            "max_concurrent_tasks": MAX_CONCURRENT_TASKS,
            "active_tasks": MAX_CONCURRENT_TASKS - semaphore._value
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")