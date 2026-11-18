"""Limitador de tasa (Rate Limiter) por ventana deslizante contra fuerza bruta y DoS."""

from collections import defaultdict, deque
import threading
import time

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """Controla el número máximo de peticiones por clave en una ventana de segundos."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, detail: str = "Demasiadas solicitudes. Intenta más tarde.") -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - (now - bucket[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=detail,
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def get_client_ip(request: Request) -> str:
    """Obtiene la IP cliente respetando X-Forwarded-For cuando hay proxy inverso."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        first_ip = forwarded.split(",")[0].strip()
        if first_ip:
            return first_ip
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


login_rate_limiter = SlidingWindowRateLimiter(max_requests=8, window_seconds=300)
register_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=600)
ai_action_rate_limiter = SlidingWindowRateLimiter(max_requests=25, window_seconds=60)


def reset_all_rate_limiters() -> None:
    login_rate_limiter.reset()
    register_rate_limiter.reset()
    ai_action_rate_limiter.reset()
