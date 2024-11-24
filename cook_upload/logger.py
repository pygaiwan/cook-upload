import sys
from pathlib import Path

from loguru import logger

logger.remove(handler_id=0)
logger.add(sys.stderr, level='INFO')
logger.add(
    Path(__file__).parent / 'cook.log',
    level='DEBUG',
    rotation='10 MB',
    retention='10 days',
    compression='zip',
)

__all__ = ['logger']
