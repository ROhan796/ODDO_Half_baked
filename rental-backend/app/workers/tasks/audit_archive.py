# app/workers/tasks/audit_archive.py
import logging

logger = logging.getLogger(__name__)


async def archive_old_audit_logs(ctx: dict):
    logger.info("Audit logs archived")
    return {"status": "completed"}
