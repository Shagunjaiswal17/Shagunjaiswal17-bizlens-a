import os
import sys

# Ensure backend directory is in python search path
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting BizLens AI Full-Stack Server on http://localhost:{port}")
    print(f"📖 Swagger Docs available at http://localhost:{port}/docs")
    print(f"📊 Dashboard UI available at http://localhost:{port}/")
    uvicorn.run(app, host="0.0.0.0", port=port)
