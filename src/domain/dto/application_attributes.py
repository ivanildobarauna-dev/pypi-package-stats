import platform
import os
from dataclasses import dataclass
from subprocess import run

result = run(["poetry version"], capture_output=True, text=True)


@dataclass
class ApplicationAttributes:
    application_name: str = "pypi-package-stats"
    application_version: str = result.stdout.strip().split()[1]
    environment: str = os.getenv("ENVIRONMENT", "dev")
    container_id: str = os.getenv("CONTAINER_ID", "unknown")
    container_image: str = os.getenv("CONTAINER_IMAGE", "unknown")
