"""app/modules/market_intelligence/models.py - Re-exports from career_paths for backward compatibility."""

from app.modules.career_paths.models import (
    CareerPathMarketData,
    CareerPathCompany,
    CareerPathJobOpening,
    CareerPathAlumni,
)

__all__ = [
    "CareerPathMarketData",
    "CareerPathCompany",
    "CareerPathJobOpening",
    "CareerPathAlumni",
]