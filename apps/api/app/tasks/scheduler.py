from apscheduler.schedulers.background import BackgroundScheduler


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    # Add production jobs here: catalog refresh, keyword recheck, trend snapshots.
    return scheduler
