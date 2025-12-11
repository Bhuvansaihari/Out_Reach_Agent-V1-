SendGrid/Twilio Notification System (FastAPI + Celery + Redis)
Overview :

This project provides an automated job-matching notification service using FastAPI, Celery, Redis, SendGrid (email), and Twilio (SMS).
It is designed for high-volume recruiting platforms where candidates receive job notifications as email, SMS, or both—according to their preferences stored in the database.

Features
🚀 FastAPI backend with Celery task queue for distributed processing.

📬 SendGrid HTML Email notifications with a professional template.

📱 Twilio SMS notifications, concise and candidate-friendly.

✉️ Flexible notification preferences: Only Email, Only SMS, or Both (controlled by database columns).

⚡ Supabase integration for candidate/job tracking.

🔄 Celery + Redis for reliable task queuing with automatic retry.

📊 Flower monitoring UI for real-time task tracking.

🧹 Production-ready with task persistence and error handling.

✨ Easy deployment on any server.

Project Structure
text
Out_Reach_Agent-V1-/
├── celery_app.py          # Celery configuration
├── start_worker.ps1       # Windows: Start Celery worker
├── start_flower.ps1       # Windows: Start Flower monitoring
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment template
├── README.md              # This file
└── webhook_receiver/
    ├── __init__.py
    ├── main.py            # FastAPI app (entry point, webhook, routing)
    ├── tasks.py           # Celery task definitions
    ├── database.py        # DB helpers (fetch candidate/job info & preferences)
    ├── email_template.py  # Loads and renders HTML email template
    ├── notifications.py   # (legacy) Direct SendGrid/Twilio helpers
    ├── utils.py           # Utilities (formatting, validation, etc)
    └── job_match_email.html # Professional email HTML template

Setup

1. Install Redis

Windows (MSI Installer):
- Download from: https://github.com/tporadowski/redis/releases
- Install Redis-x64-*.msi
- Redis starts automatically as a Windows service

Or use Docker:
```bash
docker run -d --name redis-server -p 6379:6379 redis:alpine
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

2. Install Python dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment variables in .env:

```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key

# Email
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=your_from_address@example.com

# SMS
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+11234567890

# Security
WEBHOOK_SECRET=your_secret

# Celery + Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_WORKER_CONCURRENCY=10
```

4. Start the application

You need to run THREE services:

Terminal 1 - FastAPI Server:
```bash
uvicorn webhook_receiver.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Celery Worker:
```bash
# Windows
.\start_worker.ps1

# Or manually
celery -A celery_app worker --loglevel=info --pool=solo
```

Terminal 3 - Flower Monitoring (Optional):
```bash
# Windows
.\start_flower.ps1

# Or manually
celery -A celery_app flower --port=5555
```

Usage

Webhooks:
Supabase fires a webhook to /webhook/job-match whenever a new job application is created.

Automatic Notification:
The system queues a Celery task that checks the candidate's notify_email and notify_sms settings and sends notifications accordingly.

Monitoring:
- Visit /health for a JSON health/status report
- Visit http://localhost:5555 for Flower monitoring UI (real-time task tracking)
- Visit /task/{task_id} to check specific task status

Task Status Endpoint:
```bash
GET /task/{task_id}
```
Returns task status, result, and execution info.

Customizing the Email Template
Edit webhook_receiver/job_match_email.html for your branding and content.

Variables use double curly braces, e.g., {{candidate_name}}.

Architecture

Celery + Redis Benefits:
- ✅ Task persistence (survive server restarts)
- ✅ Automatic retry with exponential backoff
- ✅ Horizontal scaling (add more workers)
- ✅ Real-time monitoring via Flower
- ✅ Better error handling and observability

License
See LICENSE for details.

Support
For issues or enhancements, please open an issue or submit a pull request.

Built with ❤️ using FastAPI, Celery, and Redis.