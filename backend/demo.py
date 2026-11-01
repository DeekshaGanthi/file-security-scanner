"""Opt-in loopback listener. Never mounted in the public FastAPI application.

Run inside a backend pod: python -m backend.demo
Then kubectl exec into that same pod to request localhost:8001/internal/demo/http-503.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.logging_config import RequestLoggingMiddleware

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(RequestLoggingMiddleware)


@app.get("/internal/demo/http-503")
def controlled_error(request: Request):
    request.state.controlled_failure = True
    return JSONResponse(status_code=503, content={
        "status": "controlled_error",
        "message": "Intentional HTTP 503 for monitoring verification"})


if __name__ == "__main__":
    import sys
    import uvicorn
    # kubectl exec output normally bypasses the container logging collector.
    # Write events into PID 1 stdout so the real backend container log is used.
    # Fail closed if the pod runtime does not allow this; never silently fake ingestion.
    sys.stdout = open("/proc/1/fd/1", "w", buffering=1)
    uvicorn.run(app, host="127.0.0.1", port=8001, proxy_headers=False, access_log=False)
