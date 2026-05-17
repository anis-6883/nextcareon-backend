from app.models.user import User                    # no FK deps
from app.models.career_path import CareerPath       # FK → user
from app.models.skill import Skill                  # FK → career_path
from app.models.project import Project              # FK → career_path
from app.models.resource import Resource            # FK → career_path
from app.models.milestone import Milestone          # FK → user

__all__ = [
    "User",
    "CareerPath",
    "Skill",
    "Project",
    "Resource",
    "Milestone",
]