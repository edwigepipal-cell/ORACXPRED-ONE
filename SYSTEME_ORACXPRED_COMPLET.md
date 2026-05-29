# 🧠 SYSTÈME ORACXPRED COMPLET - Documentation

## 📋 Vue d'Ensemble

Le système ORACXPRED est une plateforme complète de prédictions FIFA avec administration, gestion des abonnements, notifications, sauvegardes automatiques et sessions persistantes.

## 🏗️ Architecture

### Fichiers Principaux

- **`fifa1.py`** : Application Flask principale
- **`models.py`** : Modèles de données SQLAlchemy
- **`admin_routes.py`** : Routes d'administration
- **`user_routes.py`** : Routes utilisateur
- **`oracxpred_utils.py`** : Utilitaires système (uploads, sessions, sauvegardes)
- **`scheduled_tasks.py`** : Tâches automatiques (sauvegardes, nettoyage)
- **`ai_models_manager.py`** : Gestion des modèles IA (.pkl)

## 🔐 Gestion Administrateur

### Accès Admin

- Route: `/admin/login`
- Connexion séparée des utilisateurs normaux
- Session persistante optionnelle ("Se souvenir de moi")

### Panneau d'Administration

Route: `/admin/dashboard`

**Fonctionnalités:**
- Vue d'ensemble des statistiques
- Gestion des utilisateurs (activer/désactiver, approuver)
- Gestion des plans tarifaires dynamiques
- Gestion des prédictions
- Système de notifications
- Sauvegardes manuelles

### Gestion des Utilisateurs

- **Activer/Désactiver** : `/admin/user/<id>/toggle_active`
- **Approuver** : `/admin/user/<id>/approve`
- **Attribuer un abonnement** : `/admin/user/<id>/set_subscription`

## 💰 Système de Tarifs & Abonnements

### Plans Dynamiques

Les plans sont créés et modifiés par l'administrateur sans toucher au code.

**Plans par défaut:**
- **Plan 1 Semaine** : 3 prédictions/jour - 7 jours - 5 000 FCFA
- **Plan 1 Mois** : 3 prédictions/jour - 30 jours - 9 500 FCFA
- **Plan Longue Durée** : 3 prédictions/jour - 90 jours - 18 000 FCFA

### Gestion des Plans

- **Créer** : `/admin/plan/create`
- **Modifier** : `/admin/plan/<id>/update`
- **Désactiver** : `/admin/plan/<id>/delete`

### Limitations par Plan

Chaque utilisateur est limité au nombre de prédictions par jour défini dans son plan. Le système compte automatiquement les accès et bloque l'utilisateur lorsqu'il atteint sa limite.

## 📊 Gestion des Prédictions

### Limitations d'Accès

- Vérification automatique des limites quotidiennes
- Comptage des prédictions consultées par jour
- Blocage automatique à l'expiration de l'abonnement

### Planification

L'administrateur peut configurer:
- Nombre de prédictions par jour
- Horaires de publication
- Délais de publication

Route: `/admin/predictions/schedule`

## 🔔 Système de Notifications

### Types de Notifications

- **Globale** : Envoyée à tous les utilisateurs
- **Ciblée** : Envoyée à un utilisateur spécifique

### Paramètres

- Titre et message
- Priorité (low, normal, high, urgent)
- Type (info, warning, success, error)
- Durée d'affichage
- Canaux (prêt pour extension Telegram/WhatsApp)

### Routes

- **Créer** : `/admin/notification/create`
- **Liste** : `/admin/notifications`
- **API utilisateur** : `/notifications` (JSON)

## 💾 Persistance & Sauvegarde

### Protection des Données

- **ID unique immuable** : Chaque utilisateur a un `unique_id` (UUID) qui ne change jamais
- **Séparation code/données** : Les données utilisateurs sont indépendantes du code
- **Base de données persistante** : SQLite avec possibilité de migration vers PostgreSQL

### Sauvegardes Automatiques

- **Quotidienne** : Tous les jours à 2h du matin
- **Hebdomadaire** : Tous les dimanches à 3h du matin
- **Manuelle** : Via le panneau admin

### Restauration

Les sauvegardes sont stockées dans `backups/` avec horodatage. Chaque sauvegarde est enregistrée dans `BackupLog` pour traçabilité.

## 🔄 Sessions Persistantes

### Fonctionnement

- Token de session stocké en base de données
- Reconnexion automatique après redémarrage serveur
- Option "Se souvenir de moi" lors de la connexion
- Expiration automatique après 30 jours

### Nettoyage

Les sessions expirées sont nettoyées automatiquement tous les jours à 4h du matin.

## 📸 Upload de Photos de Profil

### Fonctionnalités

- Upload direct depuis la galerie de l'appareil
- Formats acceptés: JPG, PNG, GIF, WEBP
- Taille maximale: 5 MB
- Stockage dans `uploads/profiles/`

### Route

- **Servir les fichiers** : `/uploads/<filename>`

## 🤖 Gestion des Modèles IA

### Séparation Code/Données

Les modèles IA (.pkl) sont stockés séparément des données utilisateurs dans `ai_models/`.

### Fonctions Disponibles

- `save_model()` : Sauvegarder un modèle
- `load_model()` : Charger un modèle
- `list_models()` : Lister tous les modèles
- `delete_model()` : Supprimer un modèle

### Métadonnées

Chaque modèle a des métadonnées stockées dans `models_metadata.json`:
- Nom du modèle
- Version
- Date de création
- Métadonnées personnalisées

## 🚀 Démarrage

### Installation

```bash
pip install -r requirements.txt
```

### Initialisation

```bash
python run.py
```

### Tâches Automatiques

Pour lancer les tâches automatiques (sauvegardes, nettoyage):

```bash
python scheduled_tasks.py
```

Ou intégrer dans l'application principale avec un thread séparé.

## 🔒 Sécurité

### Sessions

- Clé secrète pour les sessions Flask
- Tokens de session persistants hashés
- Expiration automatique

### Validation

- Vérification des rôles (admin/user)
- Protection CSRF (à ajouter en production)
- Validation des uploads de fichiers

### Logs

Toutes les actions importantes sont journalisées dans `SystemLog`:
- Connexions/déconnexions
- Actions admin
- Modifications de données

## 📝 Notes Importantes

### Philosophie Technique

> Le site peut changer.  
> Le code peut évoluer.  
> Les comptes et les données, eux, sont sacrés.

### Protection des Données

- Aucun compte ne doit jamais être perdu
- Les données survivent aux refactorisations
- Les sauvegardes sont automatiques et régulières
- Possibilité de restauration complète ou partielle

## 🛠️ Maintenance

### Tâches Régulières

1. Vérifier les sauvegardes quotidiennes
2. Surveiller l'espace disque
3. Nettoyer les anciennes sauvegardes (>30 jours)
4. Vérifier les logs système

### Commandes Utiles

```python
# Nettoyer les sessions expirées
from oracxpred_utils import cleanup_expired_sessions
cleanup_expired_sessions()

# Vérifier les abonnements expirés
from oracxpred_utils import check_and_expire_subscriptions
check_and_expire_subscriptions()

# Créer une sauvegarde manuelle
from oracxpred_utils import create_backup
create_backup('manual', admin_id=1)
```

## 📞 Support

Pour toute question ou problème, consulter les logs système dans `SystemLog` ou les logs de sauvegarde dans `BackupLog`.
