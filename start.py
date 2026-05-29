#!/usr/bin/env python3
"""
Script de démarrage simple pour Render.
"""

import os
import sys
import traceback


def demarrer_application():
    """Démarre l'application Flask."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    print("🚀 Démarrage du système révolutionnaire")
    print("=" * 50)

    try:
        from fifa1 import app
    except Exception as e:
        print(f"❌ Impossible de charger l'application: {e}")
        traceback.print_exc()
        sys.exit(1)

    port = int(os.environ.get("PORT", 10000))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"🌐 Application disponible sur {host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    demarrer_application()
