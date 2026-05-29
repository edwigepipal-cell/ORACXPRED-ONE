#!/usr/bin/env python3
"""
Simple startup script for Render.
"""

import os
import subprocess
import sys
import traceback
from pathlib import Path


def _ensure_dependencies():
    """Install project dependencies if the runtime cannot import Flask yet."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        import flask  # noqa: F401
        return
    except Exception:
        pass

    requirements_path = Path(__file__).with_name("requirements.txt")
    if not requirements_path.exists():
        return

    print("Flask not detected at runtime, installing dependencies...")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(requirements_path),
        ]
    )


def demarrer_application():
    """Start the Flask application."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    print("Starting application bootstrap")
    print("=" * 50)

    try:
        _ensure_dependencies()
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
