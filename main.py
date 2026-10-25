import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"[BizLens AI] Starting Full-Stack Server on http://localhost:{port}")
    print(f"[BizLens AI] Interactive Swagger Docs: http://localhost:{port}/docs")
    print(f"[BizLens AI] Dashboard UI: http://localhost:{port}/")
    uvicorn.run(app, host="0.0.0.0", port=port)
