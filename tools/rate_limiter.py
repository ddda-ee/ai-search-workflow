import time
import threading


class RateLimiter:
    """
    单源线程安全限速器。
    用于限制特定 API 的最小请求间隔，防止触发 429 或封 IP。
    """
    def __init__(self, min_interval_seconds: float = 2.0):
        self.min_interval = min_interval_seconds
        self.last_request_time = 0.0
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            now = time.time()
            elapsed = now - self.last_request_time
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
            self.last_request_time = time.time()