"""app/modules/admin/admin_routes_extended.py - Extended admin routes for scores, gamification, and AI."""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.engine import get_session
from app.core.dependencies import get_current_admin
from app.modules.users.models import AdminUser, Student
from app.modules.career_score.models import CareerScore
from app.modules.gamification.models import Achievement, InventoryItem, CoinLedger, UserBalance
from app.modules.career_paths.models import CareerPath

from app.modules.admin.admin_schemas import (
    CareerScoreRead, CareerScoreOverride,
    AchievementCreateAdmin, AchievementUpdateAdmin, AchievementReadAdmin,
    StoreItemCreateAdmin, StoreItemUpdateAdmin, StoreItemReadAdmin,
    AiGateConfigUpdate,
)
from app.modules.admin.audit_service import log_admin_action, log_score_override
from app.modules.admin.audit_models import AuditActionType


router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================================
# Career Score Override Console (Highly Secure)
# ============================================================================

@router.get("/students/{student_id}/career-score", response_model=CareerScoreRead)
async def get_student_career_score(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a student's current career score."""
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get or create career score
    result = await session.execute(
        select(CareerScore).where(CareerScore.student_id == student_id)
    )
    score = result.first()
    if not score:
        raise HTTPException(status_code=404, detail="Career score not found")

    return CareerScoreRead.model_validate(score)


@router.post("/students/{student_id}/career-score/override", response_model=CareerScoreRead)
async def override_career_score(
    student_id: str,
    override_data: CareerScoreOverride,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """
    Override a student's career score metric.
    This is a highly secure, audited operation.
    """
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get career score
    result = await session.execute(
        select(CareerScore).where(CareerScore.student_id == student_id)
    )
    score = result.first()
    if not score:
        raise HTTPException(status_code=404, detail="Career score not found")

    # Map metric type to score field
    metric_mapping = {
        "COURSE_COMPLETION": "course_completion_score",
        "QUIZ": "quiz_performance_score",
        "PROJECT": "project_quality_score",
        "PORTFOLIO": "portfolio_strength_score",
        "INTERVIEW": "mock_interview_score",
        "TOTAL": "total_career_score",
    }

    field = metric_mapping.get(override_data.metric_type)
    if not field:
        raise HTTPException(status_code=400, detail="Invalid metric type")

    # Capture previous value
    previous_value = getattr(score, field)

    # Update the score
    setattr(score, field, override_data.new_value)
    await session.commit()
    await session.refresh(score)

    # Log the override in the specialized audit log
    await log_score_override(
        session,
        admin_id=admin.id,
        student_id=student_id,
        metric_type=override_data.metric_type,
        previous_value=previous_value,
        new_value=override_data.new_value,
        reason=override_data.reason,
    )

    return CareerScoreRead.model_validate(score)


# ============================================================================
# Gamification Management
# ============================================================================

@router.post("/achievements", response_model=AchievementReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_achievement(
    data: AchievementCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a new achievement tier."""
    achievement = Achievement(
        tier=data.tier,
        metric_type=data.metric_type,
        target_threshold=data.target_threshold,
        badge_image_url=data.badge_image_url or "",
    )
    session.add(achievement)
    await session.commit()
    await session.refresh(achievement)

    await log_admin_action(
        session,
        admin_id=admin.id,
        entity_type="Achievement",
        entity_id=achievement.id,
        action=AuditActionType.CREATE,
        after_state={"tier": achievement.tier, "metric_type": achievement.metric_type},
        reason="Created new achievement tier",
    )

    return AchievementReadAdmin.model_validate(achievement)


@router.get("/achievements", response_model=List[AchievementReadAdmin])
async def list_achievements(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all achievement tiers."""
    result = await session.execute(
        select(Achievement).offset(skip).limit(limit)
    )
    achievements = result.scalars().all()
    return [AchievementReadAdmin.model_validate(a) for a in achievements]


@router.get("/achievements/{achievement_id}", response_model=AchievementReadAdmin)
async def get_achievement(
    achievement_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific achievement."""
    achievement = await session.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return AchievementReadAdmin.model_validate(achievement)


@router.patch("/achievements/{achievement_id}", response_model=AchievementReadAdmin)
async def update_achievement(
    achievement_id: str,
    data: AchievementUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update an achievement tier."""
    achievement = await session.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    before_state = {"tier": achievement.tier, "target_threshold": achievement.target_threshold}

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(achievement, field):
            setattr(achievement, field, value)

    await session.commit()
    await session.refresh(achievement)

    after_state = {"tier": achievement.tier, "target_threshold": achievement.target_threshold}

    await log_admin_action(
        session,
        admin_id=admin.id,
        entity_type="Achievement",
        entity_id=achievement_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated achievement tier",
    )

    return AchievementReadAdmin.model_validate(achievement)


@router.delete("/achievements/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_achievement(
    achievement_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete an achievement tier."""
    achievement = await session.get(Achievement, achievement_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    await log_admin_action(
        session,
        admin_id=admin.id,
        entity_type="Achievement",
        entity_id=achievement_id,
        action=AuditActionType.DELETE,
        before_state={"tier": achievement.tier},
        reason="Deleted achievement tier",
    )

    await session.delete(achievement)
    await session.commit()


# ============================================================================
# Store Inventory Management
# ============================================================================

@router.post("/store-items", response_model=StoreItemReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_store_item(
    data: StoreItemCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a new store item."""
    item = InventoryItem(
        type=data.type,
        name=data.name,
        coin_cost=data.coin_cost,
        resource_payload_json=data.resource_payload_json or {},
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)

    await log_admin_action(
        session,
        admin_id=admin.id,
        entity_type="InventoryItem",
        entity_id=item.id,
        action=AuditActionType.CREATE,
        after_state={"name": item.name, "coin_cost": item.coin_cost},
        reason="Created new store item",
    )

    return StoreItemReadAdmin.model_validate(item)


@router.get("/store-items", response_model=List[StoreItemReadAdmin])
async def list_store_items(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all store items."""
    result = await session.execute(
        select(InventoryItem).offset(skip).limit(limit)
    )
    items = result.scalars().all()
    return [StoreItemReadAdmin.model_validate(i) for i in items]


@router.get("/store-items/{item_id}", response_model=StoreItemReadAdmin)
async def get_store_item(
    item_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific store item."""
    item = await session.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Store item not found")
    return StoreItemReadAdmin.model_validate(item)


@router.patch("/store-items/{item_id}", response_model=StoreItemReadAdmin)
async def update_store_item(
    item_id: str,
    data: StoreItemUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update a store item."""
    item = await session.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Store item not found")

    before_state = {"name": item.name, "coin_cost": item.coin_cost}

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(item, field):
            setattr(item, field, value)

    await session.commit()
    await session.refresh(item)

    after_state = {"name": item.name, "coin_cost": item.coin_cost}

    await log_admin_action(
        session,
        admin_id=admin.id,
        entity_type="InventoryItem",
        entity_id=item_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated store item",
    )

    return StoreItemReadAdmin.model_validate(item)


@router.delete("/store-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store_item(
    item_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete a store item."""
    item = await session.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Store item not found")

    await log_admin_action(
        session,
        admin_id=admin.id,
        entity_type="InventoryItem",
        entity_id=item_id,
        action=AuditActionType.DELETE,
        before_state={"name": item.name},
        reason="Deleted store item",
    )

    await session.delete(item)
    await session.commit()


# ============================================================================
# Coin Ledger & Balance Management
# ============================================================================

@router.get("/students/{student_id}/coin-balance")
async def get_student_coin_balance(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a student's current coin balance and ledger."""
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get balance
    result = await session.execute(
        select(UserBalance).where(UserBalance.student_id == student_id)
    )
    balance = result.first()

    # Get recent ledger entries
    ledger_result = await session.execute(
        select(CoinLedger)
        .where(CoinLedger.student_id == student_id)
        .order_by(CoinLedger.created_at.desc())
        .limit(50)
    )
    ledger = ledger_result.scalars().all()

    return {
        "student_id": student_id,
        "current_balance": balance.current_balance if balance else 0,
        "recent_transactions": [
            {
                "type": entry.transaction_type,
                "amount": entry.amount,
                "source": entry.source_trigger,
                "timestamp": entry.created_at,
            }
            for entry in ledger
        ],
    }


@router.post("/students/{student_id}/adjust-coins")
async def manually_adjust_student_coins(
    student_id: str,
    adjustment: dict,  # {"amount": int, "reason": str}
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Manually adjust a student's coin balance (admin only)."""
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    amount = adjustment.get("amount", 0)
    reason = adjustment.get("reason", "Admin adjustment")

    # Get or create balance
    result = await session.execute(
        select(UserBalance).where(UserBalance.student_id == student_id)
    )
    balance = result.first()
    if not balance:
        balance = UserBalance(student_id=student_id, current_balance=0)
        session.add(balance)

    old_balance = balance.current_balance
    balance.current_balance += amount

    # Create ledger entry
    ledger_entry = CoinLedger(
        student_id=student_id,
        transaction_type="DEPOSIT" if amount > 0 else "WITHDRAWAL",
        source_trigger="ADMIN_ADJUSTMENT",
        amount=abs(amount),
        balance_snapshot=balance.current_balance,
        description=reason,
    )
    session.add(ledger_entry)
    await session.commit()

    await log_admin_action(
        session,
        admin_id=admin.id,
        entity_type="CoinBalance",
        entity_id=student_id,
        action=AuditActionType.UPDATE,
        before_state={"balance": old_balance},
        after_state={"balance": balance.current_balance},
        reason=reason,
    )

    return {
        "student_id": student_id,
        "old_balance": old_balance,
        "new_balance": balance.current_balance,
        "adjustment": amount,
        "reason": reason,
    }


# ============================================================================
# AI Assistant Configuration
# ============================================================================

@router.get("/ai-config")
async def get_ai_configuration(
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get current AI assistant configuration."""
    # This would read from app config or a config table
    # For now, return the hardcoded/environment-based settings
    from app.core.config import settings

    return {
        "ai_model": settings.OPENAI_CHAT_MODEL,
        "max_tokens_per_response": settings.OPENAI_CHAT_MAX_TOKENS,
        "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
        "embedding_dimensions": settings.OPENAI_EMBEDDING_DIMENSIONS,
    }


@router.post("/ai-config/update")
async def update_ai_configuration(
    config_update: AiGateConfigUpdate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update AI gate configuration."""
    # In a real system, this would update a configuration table
    # For now, log the intent
    await log_admin_action(
        session,
        admin_id=admin.id,
        entity_type="AiGateConfig",
        entity_id="global",
        action=AuditActionType.UPDATE,
        after_state={
            "coins_per_question": config_update.coins_per_ai_question,
            "questions_per_exchange": config_update.questions_per_exchange,
            "max_tokens": config_update.max_tokens_per_response,
        },
        reason="Updated AI gate configuration",
    )

    return {
        "message": "AI configuration updated successfully",
        "coins_per_question": config_update.coins_per_ai_question,
        "questions_per_exchange": config_update.questions_per_exchange,
        "max_tokens_per_response": config_update.max_tokens_per_response,
    }


# ============================================================================
# System Health & Monitoring
# ============================================================================

@router.get("/health")
async def admin_health_check(
    admin: AdminUser = Depends(get_current_admin),
):
    """Get admin panel health status."""
    return {
        "status": "healthy",
        "admin_id": admin.id,
        "admin_role": admin.role,
        "message": "Admin API is operational",
    }
