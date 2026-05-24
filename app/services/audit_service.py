"""
Audit logging service layer for recording administrative actions.
Provides methods to create, query, and analyze audit logs.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, desc
from sqlmodel import Session

from app.models.audit_log import AdminAuditLog
from app.core.config import settings
import json


class AuditService:
    """Service for managing audit logs"""

    @staticmethod
    def log_action(
        session: Session,
        admin_id: int,
        action_type: str,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AdminAuditLog:
        """
        Log an administrative action to the audit log.
        
        Args:
            session: Database session
            admin_id: ID of the admin performing the action
            action_type: Type of action (e.g., 'COURSE_CREATED', 'USER_BANNED')
            target_type: Type of the target entity
            target_id: ID of the target entity
            details: Additional details as dictionary (will be JSON-serialized)
            status: 'success' or 'failed'
            error_message: Error message if action failed
            ip_address: IP address of requesting admin
            user_agent: User-Agent header
            
        Returns:
            Created AdminAuditLog record
        """
        # Convert details dict to JSON string
        details_json = None
        if details:
            try:
                details_json = json.dumps(details)
            except (TypeError, ValueError):
                details_json = str(details)

        audit_log = AdminAuditLog(
            admin_id=admin_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            details=details_json,
            status=status,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
        )

        session.add(audit_log)
        session.commit()
        session.refresh(audit_log)

        return audit_log

    @staticmethod
    def get_logs(
        session: Session,
        admin_id: Optional[int] = None,
        action_type: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AdminAuditLog]:
        """
        Query audit logs with optional filters.
        
        Args:
            session: Database session
            admin_id: Filter by admin ID
            action_type: Filter by action type
            target_type: Filter by target entity type
            target_id: Filter by target ID
            start_date: Start date for time range filter
            end_date: End date for time range filter
            limit: Maximum number of records to return
            offset: Offset for pagination
            
        Returns:
            List of audit log records
        """
        query = select(AdminAuditLog)

        if admin_id is not None:
            query = query.where(AdminAuditLog.admin_id == admin_id)
        if action_type is not None:
            query = query.where(AdminAuditLog.action_type == action_type)
        if target_type is not None:
            query = query.where(AdminAuditLog.target_type == target_type)
        if target_id is not None:
            query = query.where(AdminAuditLog.target_id == target_id)
        if start_date is not None:
            query = query.where(AdminAuditLog.timestamp >= start_date)
        if end_date is not None:
            query = query.where(AdminAuditLog.timestamp <= end_date)

        # Order by most recent first and apply pagination
        query = query.order_by(desc(AdminAuditLog.timestamp))
        query = query.limit(limit).offset(offset)

        return session.exec(query).all()

    @staticmethod
    def get_log_count(
        session: Session,
        admin_id: Optional[int] = None,
        action_type: Optional[str] = None,
        target_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """Get total count of audit logs matching filters."""
        query = select(func.count(AdminAuditLog.log_id))

        if admin_id is not None:
            query = query.where(AdminAuditLog.admin_id == admin_id)
        if action_type is not None:
            query = query.where(AdminAuditLog.action_type == action_type)
        if target_type is not None:
            query = query.where(AdminAuditLog.target_type == target_type)
        if start_date is not None:
            query = query.where(AdminAuditLog.timestamp >= start_date)
        if end_date is not None:
            query = query.where(AdminAuditLog.timestamp <= end_date)

        return session.exec(query).one()

    @staticmethod
    def cleanup_old_logs(session: Session, retention_days: Optional[int] = None) -> int:
        """
        Delete audit logs older than retention period.
        Useful for compliance and storage management.
        
        Args:
            session: Database session
            retention_days: Number of days to retain logs. Uses config if not provided.
            
        Returns:
            Number of records deleted
        """
        if retention_days is None:
            retention_days = settings.ADMIN_AUDIT_LOG_RETENTION_DAYS

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Get count before deletion
        count_query = select(func.count(AdminAuditLog.log_id)).where(
            AdminAuditLog.timestamp < cutoff_date
        )
        count = session.exec(count_query).one()

        # Delete old logs
        delete_query = select(AdminAuditLog).where(AdminAuditLog.timestamp < cutoff_date)
        logs_to_delete = session.exec(delete_query).all()
        for log in logs_to_delete:
            session.delete(log)
        session.commit()

        return count

    @staticmethod
    def get_action_summary(
        session: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """
        Get a summary count of actions by type within a date range.
        
        Returns:
            Dictionary with action_type as key and count as value
        """
        query = select(AdminAuditLog.action_type, func.count(AdminAuditLog.log_id))

        if start_date is not None:
            query = query.where(AdminAuditLog.timestamp >= start_date)
        if end_date is not None:
            query = query.where(AdminAuditLog.timestamp <= end_date)

        query = query.group_by(AdminAuditLog.action_type)

        results = session.exec(query).all()
        return {action_type: count for action_type, count in results}

    @staticmethod
    def get_admin_activity(
        session: Session,
        admin_id: int,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get activity summary for a specific admin over last N days.
        
        Args:
            session: Database session
            admin_id: Admin user ID
            days: Number of days to look back
            
        Returns:
            Dictionary with activity statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        total_actions = AuditService.get_log_count(
            session,
            admin_id=admin_id,
            start_date=start_date,
        )

        logs = AuditService.get_logs(
            session,
            admin_id=admin_id,
            start_date=start_date,
            limit=1000,
        )

        action_types = {}
        failed_count = 0
        
        for log in logs:
            # Count by action type
            action_types[log.action_type] = action_types.get(log.action_type, 0) + 1
            
            # Count failures
            if log.status == "failed":
                failed_count += 1

        return {
            "admin_id": admin_id,
            "days": days,
            "total_actions": total_actions,
            "failed_actions": failed_count,
            "success_rate": (total_actions - failed_count) / total_actions if total_actions > 0 else 100,
            "action_breakdown": action_types,
        }
