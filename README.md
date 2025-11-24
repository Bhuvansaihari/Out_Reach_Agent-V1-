SendGrid/Twilio Notification System (FastAPI)
Overview :

This project provides an automated job-matching notification service using FastAPI, SendGrid (email), and Twilio (SMS).
It is designed for high-volume recruiting platforms where candidates receive job notifications as email, SMS, or both—according to their preferences stored in the database.

Features
🚀 FastAPI backend with async concurrency for high throughput.

📬 SendGrid HTML Email notifications with a professional template.

📱 Twilio SMS notifications, concise and candidate-friendly.

✉️ Flexible notification preferences: Only Email, Only SMS, or Both (controlled by database columns).

⚡ Supabase integration for candidate/job tracking.

🧹 No agents/crewai—all logic handled in Python with robust, maintainable code.

✨ Easy deployment on any server.

Project Structure
text
webhook_receiver/
├── __init__.py
├── main.py             # FastAPI app (entry point, webhook, routing)
├── database.py         # DB helpers (fetch candidate/job info & preferences)
├── email_template.py   # Loads and renders HTML email template
├── notifications.py    # (optional) Direct SendGrid/Twilio helpers
├── utils.py            # Utilities (formatting, validation, etc)
├── job_match_email.html # Professional email HTML template
Setup
Clone the repository

Install dependencies

text
pip install -r requirements.txt
# or, if using poetry
poetry install
Configure environment variables in .env:

text
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=your_from_address@example.com
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+11234567890
WEBHOOK_SECRET=your_secret
MAX_CONCURRENT_TASKS=20
Start the application

text
uvicorn webhook_receiver.main:app --reload --host 0.0.0.0 --port 8000
Usage
Webhooks:
Supabase fires a webhook to /webhook/job-match whenever a new job application is created.

Automatic Notification:
The system checks the candidate’s notify_email and notify_sms settings and sends notifications accordingly.

Monitoring:
Visit /health for a JSON health/status/concurrency report.

Customizing the Email Template
Edit webhook_receiver/job_match_email.html for your branding and content.

Variables use double curly braces, e.g., {{candidate_name}}.

License
See LICENSE for details.

Support
For issues or enhancements, please open an issue or submit a pull request.

Built with ❤️ by your engineering team & FastAPI.