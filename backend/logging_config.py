"""Allowlisted JSON events; never serialize request bodies or exception text."""
import json
import sys
import time
import uuid
from datetime import datetime, timezone


def emit_event(event, message, severity="INFO", **fields):
    record = {"timestamp": datetime.now(timezone.utc).isoformat(),
              "severity": severity, "service": "backend", "event": event,
              "message": message, **fields}
    print(json.dumps(record, ensure_ascii=True, allow_nan=False), file=sys.stdout, flush=True)


class RequestLoggingMiddleware:
    """One completion per HTTP request, including safely handled exceptions."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        started = time.perf_counter()
        request_id = str(uuid.uuid4())
        for key, value in scope.get("headers", []):
            if key.lower() == b"x-request-id":
                try:
                    request_id = str(uuid.UUID(value.decode("ascii")))
                except (ValueError, UnicodeError):
                    pass
        status = 500
        response_started = False
        error = False

        async def capture(message):
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                status = message["status"]
                response_started = True
                message = {**message, "headers": [
                    (k, v) for k, v in message.get("headers", [])
                    if k.lower() != b"x-request-id"
                ] + [(b"x-request-id", request_id.encode("ascii"))]}
            await send(message)

        try:
            await self.app(scope, receive, capture)
        except Exception:
            error = True
            if response_started:
                raise
            from starlette.responses import JSONResponse
            await JSONResponse({"detail": "Internal server error"}, status_code=500)(
                scope, receive, capture)
        finally:
            route = scope.get("route")
            # Route templates preserve useful paths without attacker-controlled path data.
            path = getattr(route, "path", "<unmatched>")
            fields = dict(http_method=scope["method"], http_path=path,
                          http_status=status, duration_ms=round(
                              (time.perf_counter() - started) * 1000, 3),
                          request_id=request_id)
            if status >= 500 or error:
                fields.update(error_category="unhandled_exception" if error else "http_error",
                              error_message="Request failed")
            if scope.get("state", {}).get("controlled_failure"):
                fields["controlled_failure"] = True
            emit_event("http_request", "HTTP request completed",
                       "ERROR" if status >= 500 or error else "INFO", **fields)
