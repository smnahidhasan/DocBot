import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from typing import Callable

from app.core.logging import get_access_logger, log_with_context

access_logger = get_access_logger()
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""

    def __init__(self, app, skip_paths: list = None):
        super().__init__(app)
        self.skip_paths = skip_paths or ["/health", "/docs", "/openapi.json", "/favicon.ico"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Skip logging for certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)

        # Start timing
        start_time = time.time()

        # Get client info
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")

        # Log request
        log_with_context(
            access_logger,
            logging.INFO,
            f"Request started: {request.method} {request.url.path}",
            request_id=request_id,
            method=request.method,
            endpoint=request.url.path,
            query_params=str(request.query_params),
            ip_address=client_ip,
            user_agent=user_agent
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate response time
            response_time = time.time() - start_time

            # Log response
            log_with_context(
                access_logger,
                logging.INFO,
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                request_id=request_id,
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                response_time=round(response_time * 1000, 2),  # Convert to milliseconds
                ip_address=client_ip,
                user_agent=user_agent
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate response time for failed requests
            response_time = time.time() - start_time

            # Log error
            log_with_context(
                logger,
                logging.ERROR,
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                request_id=request_id,
                method=request.method,
                endpoint=request.url.path,
                response_time=round(response_time * 1000, 2),
                ip_address=client_ip,
                user_agent=user_agent,
                error=str(e)
            )

            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for X-Forwarded-For header (proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for X-Real-IP header (nginx)
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to client host
        if request.client:
            return request.client.host

        return "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )

        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware"""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Clean old entries (older than 1 minute)
        self.client_requests = {
            ip: timestamps for ip, timestamps in self.client_requests.items()
            if any(t > current_time - 60 for t in timestamps)
        }

        # Get client's request timestamps
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = []

        # Filter timestamps within the last minute
        self.client_requests[client_ip] = [
            t for t in self.client_requests[client_ip]
            if t > current_time - 60
        ]

        # Check rate limit
        if len(self.client_requests[client_ip]) >= self.requests_per_minute:
            log_with_context(
                logger,
                logging.WARNING,
                f"Rate limit exceeded for IP: {client_ip}",
                ip_address=client_ip,
                request_count=len(self.client_requests[client_ip])
            )

            response = Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json"
            )
            response.headers["Retry-After"] = "60"
            return response

        # Add current request timestamp
        self.client_requests[client_ip].append(current_time)

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"
    