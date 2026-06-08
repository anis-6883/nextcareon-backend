"""app/background/worker.py - ARQ worker setup."""

try:
    from arq import Worker, RedisSettings
except ImportError:
    Worker = None
    RedisSettings = None

from app.core.config import settings
from app.modules.career_score.service import recalculate_student_score


async def startup(ctx):
    """Worker startup hook."""
    pass


async def shutdown(ctx):
    """Worker shutdown hook."""
    pass


class ARQWorker:
    """ARQ worker configuration."""
    
    @staticmethod
    def get_worker():
        if Worker is None:
            raise ImportError("arq not installed")
        return Worker(
            functions=[
                {"recalculate_student_score": recalculate_student_score},
            ],
            redis_settings=RedisSettings.from_url(settings.REDIS_URL),
            startup=startup,
            shutdown=shutdown,
            max_jobs=settings.WORKER_CONCURRENCY,
            job_timeout=settings.WORKER_JOB_TIMEOUT,
        )


if __name__ == "__main__":
    ARQWorker.get_worker().run()