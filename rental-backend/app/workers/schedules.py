# app/workers/schedules.py

CRON_SCHEDULES = [
    {
        "function": "app.workers.tasks.overdue_detection:detect_overdue_rentals",
        "minute": "0",
        "hour": "0,6,12,18",
        "description": "Detect overdue rentals every 6 hours",
    },
    {
        "function": "app.workers.tasks.late_fee_calculation:calculate_late_fees",
        "minute": "15",
        "hour": "1,7,13,19",
        "description": "Calculate late fees every 6 hours",
    },
    {
        "function": "app.workers.tasks.reminder_dispatch:send_rental_reminders",
        "minute": "0",
        "hour": "8",
        "description": "Send rental ending reminders at 8 AM",
    },
    {
        "function": "app.workers.tasks.reminder_dispatch:send_payment_reminders",
        "minute": "0",
        "hour": "9",
        "description": "Send payment reminders at 9 AM",
    },
    {
        "function": "app.workers.tasks.reservation_expiry:expire_reservations",
        "minute": "*/15",
        "hour": "*",
        "description": "Expire reservations every 15 minutes",
    },
    {
        "function": "app.workers.tasks.trust_score_recalculation:recalculate_trust_scores",
        "minute": "0",
        "hour": "3",
        "description": "Recalculate trust scores daily at 3 AM",
    },
    {
        "function": "app.workers.tasks.pdf_generation:generate_pending_pdfs",
        "minute": "*/30",
        "hour": "*",
        "description": "Generate pending PDFs every 30 minutes",
    },
    {
        "function": "app.workers.tasks.email_dispatch:dispatch_pending_emails",
        "minute": "*/10",
        "hour": "*",
        "description": "Dispatch pending emails every 10 minutes",
    },
    {
        "function": "app.workers.tasks.sms_dispatch:dispatch_pending_sms",
        "minute": "*/10",
        "hour": "*",
        "description": "Dispatch pending SMS every 10 minutes",
    },
    {
        "function": "app.workers.tasks.materialized_view_refresh:refresh_materialized_views",
        "minute": "0",
        "hour": "2",
        "description": "Refresh materialized views daily at 2 AM",
    },
    {
        "function": "app.workers.tasks.audit_archive:archive_old_audit_logs",
        "minute": "0",
        "hour": "4",
        "description": "Archive old audit logs daily at 4 AM",
    },
]
