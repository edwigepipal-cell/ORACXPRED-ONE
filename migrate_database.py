"""
🔄 SCRIPT DE MIGRATION DE BASE DE DONNÉES
==========================================
Ajoute les colonnes manquantes aux tables existantes
"""

from flask import Flask
import sqlite3
import os
from models import db, User

# Créer une application Flask minimale pour la migration
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///oracxpred.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def migrate_database():
    """Migre la base de données pour ajouter les nouvelles colonnes"""
    
    with app.app_context():
        # Récupérer le chemin de la base de données
        db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
        if db_uri.startswith("sqlite:///"):
            db_path = db_uri.replace("sqlite:///", "")
            if not os.path.isabs(db_path):
                # Utiliser instance_path si le chemin est relatif
                if not os.path.exists(app.instance_path):
                    os.makedirs(app.instance_path, exist_ok=True)
                db_path = os.path.join(app.instance_path, db_path)
        else:
            print("❌ Migration supportée uniquement pour SQLite")
            return
        
        # Vérifier si la base de données existe
        if not os.path.exists(db_path):
            print(f"✅ Base de données n'existe pas encore, sera créée automatiquement")
            db.create_all()
            return
        
        # Connexion directe à SQLite pour les migrations
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Vérifier quelles colonnes existent dans la table users
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            
            print(f"📊 Colonnes existantes dans 'users': {columns}")
            
            # Ajouter is_active si elle n'existe pas
            if 'is_active' not in columns:
                print("➕ Ajout de la colonne 'is_active'...")
                cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
                print("✅ Colonne 'is_active' ajoutée")
            else:
                print("✅ Colonne 'is_active' existe déjà")
            
            # Ajouter unique_id si elle n'existe pas
            if 'unique_id' not in columns:
                print("➕ Ajout de la colonne 'unique_id'...")
                cursor.execute("ALTER TABLE users ADD COLUMN unique_id VARCHAR(36)")
                
                # Générer des unique_id pour les utilisateurs existants
                cursor.execute("SELECT id FROM users WHERE unique_id IS NULL")
                users_without_id = cursor.fetchall()
                
                import uuid
                for (user_id,) in users_without_id:
                    new_uuid = str(uuid.uuid4())
                    cursor.execute(
                        "UPDATE users SET unique_id = ? WHERE id = ?",
                        (new_uuid, user_id)
                    )
                
                # Créer un index unique sur unique_id
                try:
                    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_unique_id ON users(unique_id)")
                except:
                    pass  # L'index existe peut-être déjà
                
                print(f"✅ Colonne 'unique_id' ajoutée ({len(users_without_id)} utilisateurs mis à jour)")
            else:
                print("✅ Colonne 'unique_id' existe déjà")
            
            # Vérifier et créer les nouvelles tables
            print("\n📦 Vérification des nouvelles tables...")
            
            # Vérifier subscription_plans
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscription_plans'")
            if not cursor.fetchone():
                print("➕ Création de la table 'subscription_plans'...")
                db.create_all()
                print("✅ Table 'subscription_plans' créée")
            
            # Vérifier user_subscriptions
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_subscriptions'")
            if not cursor.fetchone():
                print("➕ Création de la table 'user_subscriptions'...")
                db.create_all()
                print("✅ Table 'user_subscriptions' créée")
            
            # Vérifier notifications
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
            if not cursor.fetchone():
                print("➕ Création de la table 'notifications'...")
                db.create_all()
                print("✅ Table 'notifications' créée")
            
            # Vérifier persistent_sessions
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persistent_sessions'")
            if not cursor.fetchone():
                print("➕ Création de la table 'persistent_sessions'...")
                db.create_all()
                print("✅ Table 'persistent_sessions' créée")
            
            # Vérifier backup_logs
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='backup_logs'")
            if not cursor.fetchone():
                print("➕ Création de la table 'backup_logs'...")
                db.create_all()
                print("✅ Table 'backup_logs' créée")
            
            # Vérifier prediction_schedules
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prediction_schedules'")
            if not cursor.fetchone():
                print("➕ Création de la table 'prediction_schedules'...")
                db.create_all()
                print("✅ Table 'prediction_schedules' créée")
            
            # Vérifier user_prediction_access
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_prediction_access'")
            if not cursor.fetchone():
                print("➕ Création de la table 'user_prediction_access'...")
                db.create_all()
                print("✅ Table 'user_prediction_access' créée")
            
            conn.commit()
            print("\n✅ Migration terminée avec succès!")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Erreur lors de la migration: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()


if __name__ == "__main__":
    print("🔄 Démarrage de la migration de la base de données...\n")
    migrate_database()
