import sys
import os
import subprocess

from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.blocking import BlockingScheduler


def run_pipeline():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running LeadFlow AI pipeline...")
    subprocess.run(["python", "backend/process_sources.py"])


scheduler = BlockingScheduler()

# Run every 10 minutes
scheduler.add_job(run_pipeline, trigger="interval", minutes=10, max_instances=1, coalesce=True, misfire_grace_time=300)
print("LeadFlow AI Scheduler Started")

run_pipeline()

scheduler.start()