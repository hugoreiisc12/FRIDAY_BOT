"""Run the FastAPI app locally with uvicorn (if installed).
Usage:
    python3 scripts/run_api.py
"""
import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import uvicorn
except Exception:
    uvicorn = None

if __name__ == '__main__':
    if not uvicorn:
        print("uvicorn not installed. Install fastapi[all] or uvicorn to run the API.")
        raise SystemExit(1)
    uvicorn.run("interfaces.api:app", host="127.0.0.1", port=8000, reload=True)
