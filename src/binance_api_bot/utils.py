from pathlib import Path
from typing import Any

from dotenv import dotenv_values


def set_env() -> dict[str, Any]:
    """Set environment variables from .env file.

    Returns
    -------
    dict[str,Any]
    """
    BASE_DIR = Path().resolve().parent
    ENV_PATH = BASE_DIR / ".env"
    env = dotenv_values(ENV_PATH)  # take environment variables from .env.
    return env
