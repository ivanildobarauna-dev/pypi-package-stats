from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LogStatus(Enum):
    OK = "OK"
    ERROR = "ERROR"


def log_extra_info(status: LogStatus, msg: str):
    return {"log_type": "custom", "status": status.value, "message": msg}
