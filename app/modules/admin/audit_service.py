"""app/modules/admin/audit_service.py - Admin audit logging service."""

from typing import Optional, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.admin.audit_models import AdminAuditLog, AdminScopeOverrideLog, AuditActionType
from datetime import datetime


async def log_admin_action(
    session: AsyncSession,
    admin_id: str,
    entity_type: str,
    entity_id: str,
    action: AuditActionType,
    before_state: Optional[Dict[str, Any]] = None,
    after_state: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AdminAuditLog:
    """
    Log an admin action to the audit log.
    
    Args:
        session: Database session
        admin_id: ID of the admin performing the action
        entity_type: Type of entity (e.g., 'Course', 'User', 'Quiz')
        entity_id: ID of the entity being modified
        action: Type of action (CREATE, UPDATE, DELETE, OVERRIDE)
        before_state: Previous state of the entity (for UPDATE)
        after_state: New state of the entity (for CREATE/UPDATE)
        reason: Optional reason for the operation
        ip_address: IP address of the request
        user_agent: User agent of the request
    
    Returns:
        The created AdminAuditLog record
    """
    delta_payload = {
        "before": before_state or {},
        "after": after_state or {},
    }

    log_entry = AdminAuditLog(
        admin_id=admin_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action_executed=action,
        delta_payload_json=delta_payload,
        reason_text=reason,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    session.add(log_entry)
    await session.commit()
    await session.refresh(log_entry)
    return log_entry


async def log_score_override(
    session: AsyncSession,
    admin_id: str,
    student_id: str,
    metric_type: str,
    previous_value: float,
    new_value: float,
    reason: str,
) -> AdminScopeOverrideLog:
    """
    Log a sensitive score override operation.
    
    Args:
        session: Database session
        admin_id: ID of the admin
        student_id: ID of the student
        metric_type: Type of metric being overridden
        previous_value: Previous value
        new_value: New value
        reason: Reason for override
    
    Returns:
        The created AdminScopeOverrideLog record
    """
    log_entry = AdminScopeOverrideLog(
        admin_id=admin_id,
        student_id=student_id,
        metric_type=metric_type,
        previous_value=previous_value,
        new_value=new_value,
        override_reason=reason,
    )

    session.add(log_entry)
    await session.commit()
    await session.refresh(log_entry)
    return log_entry


async def get_audit_logs(
    session: AsyncSession,
    entity_type: Optional[str] = None,
    admin_id: Optional[str] = None,
    action: Optional[AuditActionType] = None,
    limit: int = 100,
    offset: int = 0,
) -> list:
    """
    Query audit logs with optional filters.
    
    Args:
        session: Database session
        entity_type: Filter by entity type
        admin_id: Filter by admin ID
        action: Filter by action type
        limit: Maximum number of results
        offset: Result offset for pagination
    
    Returns:
        List of audit log entries
    """
    from sqlmodel import select

    query = select(AdminAuditLog)

    if entity_type:
        query = query.where(AdminAuditLog.entity_type == entity_type)
    if admin_id:
        query = query.where(AdminAuditLog.admin_id == admin_id)
    if action:
        query = query.where(AdminAuditLog.action_executed == action)

    query = query.order_by(AdminAuditLog.created_at.desc()).offset(offset).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()
