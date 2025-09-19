"""
Logging module - Request ID tracking & structured logging
Following STEP 0 rules: minimal, < 50 LOC
"""
import logging
import uuid
import time
from typing import Optional


class RequestLogger:
    """Logger with request ID tracking"""

    def __init__(self):
        self.logger = logging.getLogger("skinstack")
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_request(self, method: str, path: str, request_id: Optional[str] = None):
        """Log incoming request"""
        if not request_id:
            request_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.request_id = request_id
        self.logger.info(f"request_id={request_id} method={method} path={path}")
        return request_id

    def log_response(self, status_code: int, actor: str = "system"):
        """Log response with latency"""
        latency = round((time.time() - self.start_time) * 1000, 2)  # ms
        self.logger.info(
            f"request_id={self.request_id} actor={actor} "
            f"status={status_code} latency={latency}ms"
        )
        return latency


logger = RequestLogger()