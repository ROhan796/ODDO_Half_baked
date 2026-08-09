"""Seed script entrypoint forwarding to comprehensive seeder."""
import asyncio
import sys
from scripts.seed_comprehensive import seed_comprehensive

if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    asyncio.run(seed_comprehensive(reset=reset_flag))
