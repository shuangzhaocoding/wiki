"""Build redis-py compatible Redis URLs from settings or REDIS_URL."""
from __future__ import annotations

from os import getenv

from config import settings


def build_redis_url() -> str:
    """
    Build a redis URL. Normalizes Docker legacy link env vars such as
    REDIS_PORT=tcp://172.17.0.2:6379 and host values like tcp://redis.
    """
    raw = (getenv("REDIS_URL") or getattr(settings, "REDIS_URL", None) or "").strip()
    if raw:
        if raw.startswith("tcp://"):
            raw = "redis://" + raw[len("tcp://") :]
        elif raw.startswith("redis://tcp://"):
            raw = "redis://" + raw[len("redis://tcp://") :]
        return raw

    host = getattr(settings, "REDIS_HOST", None) or "127.0.0.1"
    host = str(host).strip()
    for prefix in ("tcp://", "http://", "https://"):
        if host.startswith(prefix):
            host = host[len(prefix) :].split("/")[0]
    port = getattr(settings, "REDIS_PORT", 6379)
    if isinstance(port, str):
        port = port.strip()
        if port.startswith("tcp://"):
            # e.g. tcp://redis:6379 from Docker Compose links
            rest = port[len("tcp://") :]
            if ":" in rest:
                _, port_part = rest.rsplit(":", 1)
                try:
                    port = int(port_part)
                except ValueError:
                    port = 6379
            else:
                port = 6379
        else:
            try:
                port = int(port)
            except ValueError:
                port = 6379
    db = int(getattr(settings, "REDIS_DB", 0))
    return f"redis://{host}:{port}/{db}"
