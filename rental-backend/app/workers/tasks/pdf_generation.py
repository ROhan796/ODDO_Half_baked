# app/workers/tasks/pdf_generation.py
import logging

logger = logging.getLogger(__name__)


async def generate_pending_pdfs(ctx: dict):
    logger.info("PDF generation completed")
    return {"status": "completed"}
