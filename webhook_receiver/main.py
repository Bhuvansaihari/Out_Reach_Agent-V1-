import os
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime
from webhook_receiver.utils import validate_webhook_payload

# Import Celery tasks
from webhook_receiver.tasks import send_notification_task

load_dotenv()

app = FastAPI(
    title="Email & SMS Webhook Receiver - Production (Celery)",
    description="Notification system using Celery task queue with Redis broker",
    version="7.0"
)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


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
        
        # Queue task in Celery instead of asyncio
        task = send_notification_task.delay(cand_id, requirement_id)
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "accepted",
                "message": f"Notification task queued",
                "task_id": task.id,
                "cand_id": cand_id,
                "requirement_id": requirement_id,
                "timestamp": datetime.now().isoformat()
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
        "service": "Email & SMS Webhook Receiver - Production (Celery)",
        "version": "7.0 (Celery + Redis)",
        "capabilities": ["email", "sms", "html_templates", "celery_tasks", "redis_broker"]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "email-sms-webhook-receiver-celery",
        "timestamp": datetime.now().isoformat(),
        "task_queue": "celery",
        "broker": "redis"
    }


@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a Celery task"""
    from celery.result import AsyncResult
    from celery_app import celery_app
    
    task_result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
        "info": task_result.info
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
