"""
Lightweight in-memory sliding-window rate limiter.
Protects compute-intensive endpoints (e.g. OCR and model inference) against DoS / brute-force abuse.
"""

import time
from collections import defaultdict
from typing import Dict, List
from flask import request, jsonify


class RateLimiter:

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests_log: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds

        # Prune expired timestamps
        timestamps = [ts for ts in self.requests_log[client_id] if ts > window_start]
        self.requests_log[client_id] = timestamps

        if len(timestamps) >= self.max_requests:
            return False

        self.requests_log[client_id].append(now)
        return True

    def get_client_id(self) -> str:
        # Check X-Forwarded-For if behind a reverse proxy, else remote_addr
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.remote_addr or "127.0.0.1"


# Default rate limiter for scanning operations (30 scans per minute per IP)
scan_rate_limiter = RateLimiter(max_requests=30, window_seconds=60)
