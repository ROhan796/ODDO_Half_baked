# app/worker/settings.py
"""ARQ worker settings — run with: arq app.worker.settings.WorkerSettings"""
from arq import cron
from arq.connections import RedisSettings
from app.config import settings


class WorkerSettings:
    """ARQ worker configuration."""

    # Redis connection
    redis_settings = RedisSettings.from_dsn(settings.ARQ_REDIS_URL or settings.REDIS_URL)

    # Worker settings
    functions = [
        "app.worker.tasks.send_notification",
        "app.worker.tasks.process_kyc_webhook",
        "app.worker.tasks.generate_invoice_pdf",
        "app.worker.tasks.sync_product_images",
        "app.worker.tasks.cleanup_expired_reservations",
        "app.worker.tasks.calculate_trust_scores",
    ]

    # Concurrency
    max_jobs = settings.WORKER_CONCURRENCY
    job_timeout = 300  # 5 minutes max per job
    keep_result = 3600  # Keep result for 1 hour

    # Retry settings
    max_tries = settings.WORKER_MAX_RETRIES
    retry_delay = 60  # Wait 60s between retries

    # Queue
    queue_name = "reprico:arq:queue"

    # Cron jobs (scheduled tasks)
    cron_jobs = [
        cron(
            "app.worker.tasks.cleanup_expired_reservations",
            hour={0, 6, 12, 18},  # Every 6 hours
            minute=0,
        ),
        cron(
            "app.worker.tasks.calculate_trust_scores",
            hour=3,  # 3 AM daily
            minute=0,
        ),
    ]
