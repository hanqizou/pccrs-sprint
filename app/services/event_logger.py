from app.models.system_event import SystemEvent


def log_system_event(user_id, event_type, summary, details=None, status="success"):
    return SystemEvent(
        user_id=user_id,
        event_type=event_type,
        summary=summary,
        details=details or {},
        status=status,
    )

