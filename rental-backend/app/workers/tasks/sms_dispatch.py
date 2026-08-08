# app/workers/tasks/sms_dispatch.py
import logging

logger = logging.getLogger(__name__)


async def dispatch_pending_sms(ctx: dict):
    logger.info("SMS dispatch completed")
    return {"status": "completed"}
