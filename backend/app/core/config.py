from dotenv import load_dotenv
import os

load_dotenv()


def _getenv(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or str(value).strip() == "":
        return default
    return str(value).strip()


def _getint(name: str, default: int) -> int:
    try:
        return int(_getenv(name, str(default)))
    except ValueError:
        return default


def _getbool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or str(raw).strip() == "":
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = _getenv("SECRET_KEY", "BuildTrackLocalSecretKeyChangeInProduction")
ALGORITHM = _getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = _getint("ACCESS_TOKEN_EXPIRE_MINUTES", 60)

# Frontend URL used inside password-reset emails.
FRONTEND_BASE_URL = _getenv("FRONTEND_BASE_URL", "http://localhost:4200")

# Password-reset email behavior.
# Keep this true only for local testing without SMTP. Set it to false in real use.
BUILDTRACK_EXPOSE_RESET_LINK = _getbool("BUILDTRACK_EXPOSE_RESET_LINK", False)

# SMTP configuration. These are optional until you enable real email sending.
SMTP_HOST = _getenv("SMTP_HOST", "")
SMTP_PORT = _getint("SMTP_PORT", 587)
SMTP_USERNAME = _getenv("SMTP_USERNAME", _getenv("SMTP_USER", ""))
SMTP_PASSWORD = _getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = _getenv("SMTP_FROM_EMAIL", _getenv("SMTP_FROM", SMTP_USERNAME))
SMTP_FROM_NAME = _getenv("SMTP_FROM_NAME", "BuildTrack")
SMTP_USE_TLS = _getbool("SMTP_USE_TLS", _getbool("SMTP_TLS", True))
SMTP_USE_SSL = _getbool("SMTP_USE_SSL", _getbool("SMTP_SSL", False))
SMTP_TIMEOUT_SECONDS = _getint("SMTP_TIMEOUT_SECONDS", 15)
SMTP_DEBUG = _getbool("SMTP_DEBUG", False)
