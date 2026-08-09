#!/usr/bin/env python
"""Run ARQ worker — start with: python run_worker.py"""
import sys
import os

# Ensure the app is importable
sys.path.insert(0, os.path.dirname(__file__))

from arq import run_worker
from app.worker.settings import WorkerSettings


if __name__ == "__main__":
    print("Starting ARQ worker for Reprico...")
    print(f"Redis: {WorkerSettings.redis_settings.host}:{WorkerSettings.redis_settings.port}")
    print(f"Concurrency: {WorkerSettings.max_jobs}")
    print(f"Functions: {len(WorkerSettings.functions)}")
    print(f"Cron jobs: {len(WorkerSettings.cron_jobs)}")
    run_worker(WorkerSettings)
