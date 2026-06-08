"""app/modules/gamification/router.py - Gamification API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import get_session
from app.core.dependencies import get_current_student
from app.modules.gamification.schemas import (
    BalanceResponse,
    LeaderboardResponse,
    PurchaseRequest,
    PurchaseResponse,
    AiExchangeResponse,
    AchievementResponse,
    StoreItemResponse,
)
from app.modules.gamification.service import (
    get_balance,
    get_leaderboard_top_n,
    purchase_item,
    exchange_ai_credits,
    get_student_achievements,
    get_store_items,
)
from app.modules.gamification.models import AiCreditGate

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/balance", response_model=BalanceResponse)
async def get_balance_endpoint(
    student=Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    """Get current student's coin balance."""
    balance = await get_balance(session, str(student.id))
    return BalanceResponse(student_id=str(student.id), balance=balance)


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard_endpoint(n: int = 100):
    """Get top N students from global leaderboard."""
    entries = await get_leaderboard_top_n(n)
    return LeaderboardResponse(entries=entries)


@router.post("/shop/unlock", response_model=PurchaseResponse)
async def purchase_item_endpoint(
    request: PurchaseRequest,
    student=Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    """Purchase an item from the shop."""
    success, msg = await purchase_item(session, str(student.id), request.item_id)
    return PurchaseResponse(success=success, message=msg)


@router.get("/shop/items", response_model=list[StoreItemResponse])
async def get_store_items_endpoint(session: AsyncSession = Depends(get_session)):
    """Get all available store items."""
    items = await get_store_items(session)
    return [StoreItemResponse(**item) for item in items]


@router.post("/ai/exchange", response_model=AiExchangeResponse)
async def exchange_ai_credits_endpoint(
    student=Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    """Exchange 100 coins for 10 AI questions."""
    success, msg = await exchange_ai_credits(session, str(student.id))
    
    ai_gate_result = (await session.exec(
        select(AiCreditGate).where(AiCreditGate.student_id == str(student.id))
    )).first()
    remaining = ai_gate_result.remaining_ai_questions if ai_gate_result else 0
    
    return AiExchangeResponse(success=success, message=msg, remaining_ai_questions=remaining)


@router.get("/achievements", response_model=list[AchievementResponse])
async def get_achievements_endpoint(
    student=Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    """Get all achievements unlocked by the student."""
    achievements = await get_student_achievements(session, str(student.id))
    return [AchievementResponse(**a) for a in achievements]