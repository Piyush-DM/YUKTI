"""Client key generation, hashing, and request rate limiting."""

import hashlib
import secrets
import threading
import time
from collections import defaultdict, deque

KEY_PREFIX = "yk_live_"


def generate_key():
    """A new client key: 256 bits of randomness, recognisable by its prefix."""
    return KEY_PREFIX + secrets.token_urlsafe(32)


def hash_key(key):
    """SHA-256 of the key.

    A fast hash is correct here, unlike for passwords: the key is 256 random
    bits, so there is nothing to brute-force, and the digest is what the
    database indexes on.
    """
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def display_prefix(key):
    """A short, non-secret fragment to recognise a key by in listings."""
    return key[: len(KEY_PREFIX) + 6]


class RateLimiter:
    """Sliding-window request limiter, per key, in memory.

    Enough for one process serving a handful of clients. State resets on
    restart and is not shared between processes.
    """

    def __init__(self, per_minute, window_seconds=60.0, clock=time.monotonic):
        self.per_minute = per_minute
        self.window = window_seconds
        self._clock = clock
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, identity):
        """Return ``(allowed, retry_after_seconds)``."""
        now = self._clock()
        with self._lock:
            hits = self._hits[identity]
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= self.per_minute:
                return False, max(1, int(self.window - (now - hits[0])) + 1)
            hits.append(now)
            return True, 0
