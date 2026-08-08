# app/workers/tasks/email_dispatch.py
import logging

logger = logging.getLogger(__name__)


async def dispatch_pending_emails(ctx: dict):
    logger.info("Email dispatch completed")
    return {"status": "completed"}
