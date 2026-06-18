from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def refresh_views(database):
    await database.execute("SELECT refresh_dashboard_views()")


def start_scheduler(database):
    scheduler.add_job(
        refresh_views,
        "interval",
        minutes=5,
        args=[database]
    )

    scheduler.start()