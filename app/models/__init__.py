
# Import order: parent tables before child tables (no FK violations).

from app.models.user import User                        # no FK deps
from app.models.admin import Admin                      # no FK deps
from app.models.career_path import CareerPath           # FK → user
from app.models.skill import Skill                      # FK → career_path
from app.models.project import Project                  # FK → career_path
from app.models.resource import Resource                # FK → career_path
from app.models.milestone import Milestone              # FK → user
from app.models.course import Course                    # FK → career_path
from app.models.audit_log import AdminAuditLog          # FK → user
from app.models.user_warning import UserWarning         # FK → user

__all__ = [
    "User",
    "Admin",
    "CareerPath",
    "Skill",
    "Project",
    "Resource",
    "Milestone",
    "Course",
    "AdminAuditLog",
    "UserWarning",
]