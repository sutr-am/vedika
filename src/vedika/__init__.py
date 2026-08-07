import json
import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    # 1. REMOVED the <level> wrapper around {message} here
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>[VEDIKA]</cyan> {message}",
    level="INFO",
    colorize=True,  # 2. ADDED this to force colors in Warp/just
)


def log_json_dict(data: dict, message: str):
    data_formatted = json.dumps(data, indent=4)
    # 3. ADDED color tags (e.g., <yellow>) around the data variable
    logger.opt(colors=True).info(f"{message}:\n<yellow>{data_formatted}</yellow>")
