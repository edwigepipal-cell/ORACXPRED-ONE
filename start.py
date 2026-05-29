#!/usr/bin/env python3
"""
Simple startup script for Render.
"""

import os
import site
import subprocess
import sys
import traceback
from pathlib import Path


def _bootstrap_paths():
    """Ensure the project and user site-packages are importable."""
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir))

    user_site = site.getusersitepackages()
    if user_site and user_site not in sys.path:
        site.addsitedir(user_site)


def _install_missing_dependencies():
    """Install requirements into the user site when the runtime misses Flask."""
    try:
        import flask  # noqa: F401
        return
    except Exception:
        pass

    requirements_path = Path(__file__).with_name("requirements.txt")
    if not requirements_path.exists():
        return

    print("Flask not detected at runtime, installing dependencies with --user...")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--user",
            "--disable-pip-version-check",
            "-r",
            str(requirements_path),
        ]
    )

    _bootstrap_paths()


def demarrer_application():
    """Start the Flask application."""
    _bootstrap_paths()

    print("Starting application bootstrap")
    print("=" * 50)

    try:
        _install_missing_dependencies()
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
