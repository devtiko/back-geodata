import logging

from src.core.settings import settings

logging.basicConfig(
  level=settings.LOG_LEVEL,
  format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
  datefmt="%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str) -> logging.Logger:
  return logging.getLogger(name)
