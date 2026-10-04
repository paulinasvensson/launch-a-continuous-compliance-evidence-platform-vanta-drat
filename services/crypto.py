import os
from cryptography.fernet import Fernet

_KEY = os.environ.get("TOKEN_ENCRYPTION_KEY")
if not _KEY:
    # dev-only fallback key so the app runs out of the box; set
    # TOKEN_ENCRYPTION_KEY in production.
    _KEY = "dOq1q8f6b8lQe2b9b1h9x1b1kQe2b9b1h9x1b1kQe2A="

try:
    _fernet = Fernet(_KEY)
except Exception:
    _fernet = Fernet(Fernet.generate_key())


def encrypt_token(raw: str) -> str:
    return _fernet.encrypt(raw.encode()).decode()


def decrypt_token(token: str) -> str:
    return _fernet.decrypt(token.encode()).decode()
