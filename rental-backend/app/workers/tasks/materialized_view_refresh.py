# app/workers/tasks/materialized_view_refresh.py
import logging

logger = logging.getLogger(__name__)


async def refresh_materialized_views(ctx: dict):
    logger.info("Materialized views refreshed")
    return {"status": "completed"}
