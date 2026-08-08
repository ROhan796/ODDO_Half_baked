"""ARQ worker settings."""
from arq.connections import RedisSettings
from app.config import settings


class WorkerSettings:
    functions = []
    redis_settings = RedisSettings.from_dsn(
        settings.ARQ_REDIS_URL or settings.REDIS_URL
    )
    max_jobs = settings.WORKER_CONCURRENCY
    max_tries = settings.WORKER_MAX_RETRIES
    job_timeout = 300
    keep_result = 3600
    queue_create_timeout = 10
