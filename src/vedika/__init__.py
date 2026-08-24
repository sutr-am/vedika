import json
import os
import sys

from loguru import logger

# 1. Remove default handlers
logger.remove()

# 2. Check environment
is_production = os.getenv("ENVIRONMENT", "local").lower() == "production"

if is_production:
    # Production: Structured JSON logging (No colors, outputs to stdout)
    logger.add(
        sys.stdout,
        serialize=True,
        level="INFO",
        enqueue=True,
    )
else:
    # Local: Your existing custom format optimized for Warp/just
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>[VEDIKA]</cyan> {message}",
        level="INFO",
        colorize=True,
    )


def log_json_dict(data: dict, message: str):
    """Logs a dictionary cleanly depending on the environment."""
    if is_production:
        # In production, dump it on a single line so it stays within the JSON log structure
        logger.info(f"{message}: {json.dumps(data)}")
    else:
        # Local development: Your existing colorful multi-line format
        data_formatted = json.dumps(data, indent=4)
        logger.opt(colors=True).info(f"{message}:\n<yellow>{data_formatted}</yellow>")
