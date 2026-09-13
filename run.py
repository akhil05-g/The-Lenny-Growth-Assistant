"""Single-command runner for The Lenny Growth Assistant.

Runs FastAPI with auto-reload, serving both the REST/SSE API and the React frontend.
Usage:
    python run.py
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("   The Lenny Growth Assistant — Unified Server")
    print("   • Local UI:       http://127.0.0.1:8000")
    print("   • Swagger Docs:   http://127.0.0.1:8000/docs")
    print("   • Health Status:  http://127.0.0.1:8000/api/health")
    print("=" * 65)

    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
