#!/usr/bin/env python3
"""
Simple startup script for Render.
"""

import os
import sys
import traceback
from pathlib import Path


def _reexec_into_virtualenv():
    """Run the app inside the build-time virtualenv when available."""
    base_dir = Path(__file__).resolve().parent
    venv_python = base_dir / ".venv" / "bin" / "python"

    if not venv_python.exists():
        return

    current_python = Path(sys.executable).resolve()
    if current_python == venv_python.resolve():
        return

    print(f"Switching to virtualenv Python: {venv_python}")
    os.execv(str(venv_python), [str(venv_python), str(base_dir / "start.py"), *sys.argv[1:]])


def demarrer_application():
    """Start the Flask application."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    print("Starting application bootstrap")
    print("=" * 50)

    try:
        _reexec_into_virtualenv()
        from fifa1 import app
    except Exception as e:
        print(f"Unable to load application: {e}")
        traceback.print_exc()
        sys.exit(1)

    port = int(os.environ.get("PORT", 10000))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"Application available on {host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    demarrer_application()
