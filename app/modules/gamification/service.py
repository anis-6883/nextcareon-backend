"""app/modules/gamification/service.py - Gamification service for coin transactions and achievements."""

from datetime import datetime
from typing import Optional, Tuple
from sqlmodel import select, update
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.gamification.models import (
    CoinLedger,
    UserBalance,
    Achievement,
    UserAchievement,
    InventoryItem,
    StudentInventory,
    AiCreditGate,
    TransactionType,
    SourceTrigger,
    AchievementTier,
    MetricType,
    ItemType,
)
from app.cache.redis import redis_client
from app.db.engine import engine


COIN_REWARDS = {
    "lesson_completion": 10,
    "quiz_pass": 25,
    "assignment_completion": 100,
    "project_completion": 300,
    "course_completion": 500,
}

AI_CREDIT_COST = 100
AI_QUESTIONS_PER_EXCHANGE = 10


async def get_or_create_balance(session: AsyncSession, student_id: str) -> UserBalance:
    """Get or create user balance record."""
    balance = (await session.exec(
        select(UserBalance).where(UserBalance.student_id == student_id)
    )).first()
    
    if not balance:
        balance = UserBalance(student_id=student_id, current_balance=0)
        session.add(balance)
        await session.commit()
        await session.refresh(balance)
    
    return balance


async def deposit_coins(
    session: AsyncSession,
    student_id: str,
    amount: int,
    source: SourceTrigger,
    description: str,
) -> CoinLedger:
    """
    Deposit coins to student's balance with append-only ledger.
    Updates balance and Redis leaderboard atomically.
    """
    balance = await get_or_create_balance(session, student_id)
    new_balance = balance.current_balance + amount
    
    ledger_entry = CoinLedger(
        student_id=student_id,
        transaction_type=TransactionType.DEPOSIT,
        source_trigger=source,
        amount=amount,
        balance_snapshot=new_balance,
        description=description,
    )
    session.add(ledger_entry)
    
    balance.current_balance = new_balance
    balance.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(ledger_entry)
    await session.refresh(balance)
    
    await redis_client.zadd("leaderboard:global", {student_id: new_balance})
    
    await check_and_unlock_achievements(session, student_id)
    
    return ledger_entry


async def withdraw_coins(
    session: AsyncSession,
    student_id: str,
    amount: int,
    source: SourceTrigger,
    description: str,
) -> Tuple[bool, str]:
    """
    Withdraw coins from student's balance.
    Returns (success, message) tuple.
    """
    balance = await get_or_create_balance(session, student_id)
    
    if balance.current_balance < amount:
        return False, "Insufficient coin balance"
    
    new_balance = balance.current_balance - amount
    
    ledger_entry = CoinLedger(
        student_id=student_id,
        transaction_type=TransactionType.WITHDRAWAL,
        source_trigger=source,
        amount=amount,
        balance_snapshot=new_balance,
        description=description,
    )
    session.add(ledger_entry)
    
    balance.current_balance = new_balance
    balance.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(ledger_entry)
    await session.refresh(balance)
    
    await redis_client.zadd("leaderboard:global", {student_id: new_balance})
    
    return True, "Withdrawal successful"


async def get_balance(session: AsyncSession, student_id: str) -> int:
    """Get student's current coin balance."""
    balance = await get_or_create_balance(session, student_id)
    return balance.current_balance


async def get_leaderboard_top_n(n: int = 100) -> list:
    """Get top N students from leaderboard."""
    results = await redis_client.zrevrange(
        "leaderboard:global", 0, n - 1, withscores=True
    )
    return [
        {"student_id": sid, "coins": int(score)}
        for sid, score in results
    ]


async def purchase_item(
    session: AsyncSession,
    student_id: str,
    item_id: str,
) -> Tuple[bool, str]:
    """Purchase an item from the shop."""
    item = session.get(InventoryItem, item_id)
    if not item:
        return False, "Item not found"
    
    balance = await get_or_create_balance(session, student_id)
    if balance.current_balance < item.coin_cost:
        return False, "Insufficient coins"
    
    new_balance = balance.current_balance - item.coin_cost
    
    student_inventory = StudentInventory(student_id=student_id, item_id=item_id)
    session.add(student_inventory)
    
    ledger_entry = CoinLedger(
        student_id=student_id,
        transaction_type=TransactionType.WITHDRAWAL,
        source_trigger=SourceTrigger.TEMPLATE_UNLOCK,
        amount=item.coin_cost,
        balance_snapshot=new_balance,
        description=f"Purchased {item.name}",
    )
    session.add(ledger_entry)
    
    balance.current_balance = new_balance
    balance.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(student_inventory)
    await session.refresh(ledger_entry)
    await session.refresh(balance)
    
    await redis_client.zadd("leaderboard:global", {student_id: new_balance})
    
    return True, "Item purchased successfully"


async def exchange_ai_credits(
    session: AsyncSession,
    student_id: str,
) -> Tuple[bool, str]:
    """Exchange 100 coins for 10 AI questions."""
    success, msg = await withdraw_coins(
        session,
        student_id,
        AI_CREDIT_COST,
        SourceTrigger.AI_GATE_PURCHASE,
        "AI question credits exchange",
    )
    
    if not success:
        return False, msg
    
    ai_gate = (await session.exec(
        select(AiCreditGate).where(AiCreditGate.student_id == student_id)
    )).first()
    
    if not ai_gate:
        ai_gate = AiCreditGate(student_id=student_id, remaining_ai_questions=0)
        session.add(ai_gate)
    
    ai_gate.remaining_ai_questions += AI_QUESTIONS_PER_EXCHANGE
    await session.commit()
    await session.refresh(ai_gate)
    
    return True, f"Received {AI_QUESTIONS_PER_EXCHANGE} AI questions"


async def check_and_unlock_achievements(session: AsyncSession, student_id: str):
    """Check if student has unlocked new achievements."""
    achievements = (await session.exec(select(Achievement))).all()
    user_achievements = (await session.exec(
        select(UserAchievement).where(UserAchievement.student_id == student_id)
    )).all()
    unlocked_achievement_ids = {ua.achievement_id for ua in user_achievements}
    
    for achievement in achievements:
        if achievement.id in unlocked_achievement_ids:
            continue
        
        threshold_met = False
        
        if achievement.metric_type == MetricType.COINS_EARNED:
            balance = await get_or_create_balance(session, student_id)
            threshold_met = balance.current_balance >= achievement.target_threshold
        
        if threshold_met:
            user_achievement = UserAchievement(
                student_id=student_id,
                achievement_id=achievement.id,
            )
            session.add(user_achievement)
    
    if any(a.metric_type == MetricType.COINS_EARNED for a in achievements if a.id not in unlocked_achievement_ids):
        await session.commit()


async def create_achievement(
    session: AsyncSession,
    tier: AchievementTier,
    metric_type: MetricType,
    target_threshold: int,
    badge_image_url: str,
) -> Achievement:
    """Create a new achievement definition."""
    achievement = Achievement(
        tier=tier,
        metric_type=metric_type,
        target_threshold=target_threshold,
        badge_image_url=badge_image_url,
    )
    session.add(achievement)
    await session.commit()
    await session.refresh(achievement)
    return achievement


async def get_student_achievements(session: AsyncSession, student_id: str) -> list:
    """Get all achievements unlocked by a student."""
    user_achievements = (await session.exec(
        select(UserAchievement)
        .where(UserAchievement.student_id == student_id)
        .join(Achievement)
        .order_by(Achievement.tier)
    )).all()
    
    return [
        {
            "id": ua.achievement.id,
            "tier": ua.achievement.tier,
            "metric_type": ua.achievement.metric_type,
            "target_threshold": ua.achievement.target_threshold,
            "badge_image_url": ua.achievement.badge_image_url,
            "unlocked_at": ua.unlocked_at,
        }
        for ua in user_achievements
    ]


async def create_inventory_item(
    session: AsyncSession,
    item_type: ItemType,
    name: str,
    coin_cost: int,
    resource_payload: dict,
) -> InventoryItem:
    """Create a new inventory item."""
    item = InventoryItem(
        type=item_type,
        name=name,
        coin_cost=coin_cost,
        resource_payload_json=resource_payload,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_store_items(session: AsyncSession) -> list:
    """Get all available store items."""
    items = (await session.exec(select(InventoryItem))).all()
    return [
        {
            "id": item.id,
            "type": item.type,
            "name": item.name,
            "coin_cost": item.coin_cost,
            "resource_payload": item.resource_payload_json,
        }
        for item in items
    ]