#!/usr/bin/env python3
"""
Simple startup script for Render.
"""

import os
import subprocess
import sys
import traceback
from pathlib import Path


def _bootstrap_paths():
    """Ensure the project directory is importable."""
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir))


def _venv_candidates():
    base_dir = Path(__file__).resolve().parent
    return [
        base_dir / ".venv" / "bin" / "python",
        base_dir / ".runtime_venv" / "bin" / "python",
    ]


def _current_python_is_venv_python():
    current_python = Path(sys.executable).resolve()
    return any(current_python == candidate.resolve() for candidate in _venv_candidates() if candidate.exists())


def _active_venv_python():
    for candidate in _venv_candidates():
        if candidate.exists():
            return candidate
    return None


def _ensure_virtualenv():
    """Create a local virtualenv and install requirements when needed."""
    requirements_path = Path(__file__).with_name("requirements.txt")
    if not requirements_path.exists():
        return

    active_python = _active_venv_python()
    if active_python is not None:
        try:
            subprocess.check_call(
                [
                    str(active_python),
                    "-c",
                    "import flask",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except Exception:
            pass

    base_dir = Path(__file__).resolve().parent
    runtime_venv_dir = base_dir / ".runtime_venv"
    runtime_venv_python = runtime_venv_dir / "bin" / "python"

    if not runtime_venv_python.exists():
        print("Creating runtime virtualenv...")
        subprocess.check_call([sys.executable, "-m", "venv", str(runtime_venv_dir)])

    print("Installing runtime dependencies into virtualenv...")
    subprocess.check_call([str(runtime_venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([str(runtime_venv_python), "-m", "pip", "install", "-r", str(requirements_path)])

    os.execv(str(runtime_venv_python), [str(runtime_venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])


def _maybe_switch_to_existing_venv():
    """Switch to an already-created virtualenv when possible."""
    if _current_python_is_venv_python():
        return

    active_python = _active_venv_python()
    if active_python is None:
        return

    print(f"Switching to virtualenv Python: {active_python}")
    os.execv(str(active_python), [str(active_python), str(Path(__file__).resolve()), *sys.argv[1:]])


def demarrer_application():
    """Start the Flask application."""
    _bootstrap_paths()

    print("Starting application bootstrap")
    print("=" * 50)

    try:
        _maybe_switch_to_existing_venv()
        _ensure_virtualenv()
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
