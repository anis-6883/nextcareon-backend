"""scripts/seed_db.py - Database seeding script."""

import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import async_session, init_db
from app.modules.admin.service import create_first_admin
from app.modules.gamification.models import CoinRule
from app.core.config import settings


async def seed_coin_rules(session: AsyncSession) -> None:
    """Seed coin reward rules."""
    rules = [
        CoinRule(action_type="watch_lesson", coin_reward=settings.COIN_LESSON_COMPLETE),
        CoinRule(action_type="pass_quiz", coin_reward=settings.COIN_QUIZ_PASS),
        CoinRule(action_type="complete_assignment", coin_reward=settings.COIN_ASSIGNMENT_COMPLETE),
        CoinRule(action_type="complete_project", coin_reward=settings.COIN_PROJECT_COMPLETE),
        CoinRule(action_type="complete_course", coin_reward=settings.COIN_COURSE_COMPLETE),
    ]
    for rule in rules:
        session.add(rule)
    await session.commit()


async def main() -> None:
    """Run all seeders."""
    await init_db()
    async with async_session() as session:
        # Create first admin
        await create_first_admin(session)
        # Seed coin rules
        await seed_coin_rules(session)
    print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())