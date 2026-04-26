import asyncio
import random
import logging

logger = logging.getLogger(__name__)

async def random_delay(min_sec: float, max_sec: float):
    """Random delay between actions"""
    delay = random.uniform(min_sec, max_sec)
    logger.debug(f"Waiting {delay:.1f}s")
    await asyncio.sleep(delay)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )