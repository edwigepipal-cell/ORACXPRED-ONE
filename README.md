# 🏆 Sports Betting - Application Avancée de Paris Sportifs

Une application web complète de paris sportifs avec intelligence artificielle, prédictions avancées et fonctionnalités modernes.

## 🚀 Fonctionnalités Principales

### 🔐 **Système d'Authentification Complet**
- **Comptes utilisateurs** avec niveaux d'accès (Gratuit, Premium, VIP)
- **Système d'administration** avec approbation des utilisateurs
- **Rôles** : Utilisateur, Admin, Super Admin
- **Connexion sécurisée** avec sessions persistantes
- **Synchronisation multi-appareils** automatique
- **Gestion des préférences** utilisateur

### 🎨 **Interface Moderne**
- **Mode sombre/clair** avec toggle automatique
- **Design responsive** optimisé mobile
- **Thèmes personnalisables** avec variables CSS
- **Animations fluides** et micro-interactions

### ⭐ **Système de Favoris**
- **Équipes favorites** avec suivi personnalisé
- **Ligues préférées** pour filtrage rapide
- **Page dédiée** aux matchs favoris
- **Gestion CRUD complète** via API

### 📊 **Prédictions IA Avancées**
- **6 algorithmes de prédiction** différents
- **Centre de prédictions spécialisées** par catégorie :
  - 🔢 Pair/Impair
  - ⚽ Corners
  - ⏰ Mi-temps
  - ⚖️ Handicaps
  - 📊 Totaux (Over/Under)
  - 📋 Autres paris
- **Barres de probabilité** visuelles
- **Badges de confiance** (Élevée/Moyenne/Faible)

### 📈 **Graphiques Interactifs**
- **6 types de graphiques** avec Chart.js :
  - Statistiques des équipes
  - Évolution des cotes
  - Prédictions comparatives
  - Analyse comparative
  - IA prédictive
  - Scénarios de match
- **Mode plein écran** pour chaque graphique
- **Export des données** en image

### 🔄 **Rafraîchissement Temps Réel**
- **Mise à jour automatique** toutes les 5 secondes
- **AJAX silencieux** sans rechargement de page
- **Indicateurs visuels** de statut de connexion
- **Retry automatique** en cas d'erreur
- **Pause intelligente** quand l'onglet est inactif

### 🗄️ **Base de Données Avancée**
- **SQLite** intégré pour le développement
- **Historique des matchs** complet
- **Logs des prédictions** avec tracking de précision
- **Sessions utilisateur** pour synchronisation
- **Sauvegarde automatique** des données

### ⚡ **Cache Intelligent**
- **Redis** pour cache haute performance (optionnel)
- **Cache mémoire** de fallback
- **Invalidation automatique** des données
- **Optimisation des requêtes** API

### 🔧 **API REST Complète**
- **Endpoints sécurisés** pour toutes les fonctionnalités
- **Gestion des préférences** utilisateur
- **CRUD des favoris** complet
- **Synchronisation des données** multi-appareils
- **Logs et analytics** en temps réel

## 🛠️ Installation

### Méthode Automatique (Recommandée)
```bash
python install_dependencies.py
python fifa1.py
```

### Méthode Manuelle
```bash
pip install -r requirements.txt
python fifa1.py
```

### Avec Utilisateurs de Test (Pour Administration)
```bash
python fifa1.py
# Dans un autre terminal :
python create_test_users.py
```

### Avec Redis (Optionnel pour cache)
```bash
# Windows
# Télécharger Redis depuis https://github.com/microsoftarchive/redis/releases

# Linux/Mac
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                 # macOS

# Démarrer Redis
redis-server
```

### Base de données Supabase
L'application est compatible avec une base PostgreSQL Supabase via variables d'environnement.

Variables recommandées :
- `SUPABASE_DATABASE_URL`
- `SUPABASE_POOLER_URL`
- `SUPABASE_POSTGRES_URL`
- `DATABASE_URL` en secours local

Exemple :
```bash
SUPABASE_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.bxdjgmgddwqmtwkuyiag.supabase.co:5432/postgres?sslmode=require
SUPABASE_POOLER_URL=postgresql://postgres.bxdjgmgddwqmtwkuyiag:YOUR_PASSWORD@aws-0-eu-west-1.pooler.supabase.com:6543/postgres?sslmode=require
```

Le service utilise automatiquement :
- PostgreSQL/Supabase si l'URL est fournie
- SQLite en fallback local si aucune URL distante n'est définie

Le pilote PostgreSQL est inclus dans `requirements.txt`.

## 🌐 Accès à l'Application

Une fois démarrée, l'application est accessible sur :
- **Local** : http://localhost:5000
- **Réseau** : http://192.168.x.x:5000

## 👥 Niveaux d'Utilisateur

### 🆓 **Gratuit**
- Accès aux prédictions de base
- Visualisation des matchs
- Fonctionnalités limitées
- **Nécessite approbation admin**

### 💎 **Premium** (Assigné par admin)
- Prédictions avancées
- Historique personnel
- Favoris illimités
- Graphiques complets

### 👑 **VIP** (Assigné par admin)
- Toutes les fonctionnalités
- Support prioritaire
- API access
- Analytics avancés

## 🛡️ Administration

### Rôles d'Administration
- **👤 Utilisateur** : Accès standard
- **🛡️ Admin** : Gestion des utilisateurs et quotas
- **👑 Super Admin** : Contrôle total du système

### Compte Admin Par Défaut
```
👤 Nom d'utilisateur : admin
🔑 Mot de passe : admin123
⚠️ CHANGEZ LE MOT DE PASSE IMMÉDIATEMENT !
```

### Fonctionnalités Admin
- **Approbation des nouveaux utilisateurs**
- **Attribution des niveaux Premium/VIP**
- **Gestion des rôles administrateurs**
- **Logs et audit complet**
- **Statistiques détaillées**

## 🔧 Configuration

### Variables d'Environnement
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///sports_betting.db
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Base de Données
La base de données SQLite est créée automatiquement au premier démarrage avec toutes les tables nécessaires.

## 📱 Fonctionnalités Mobiles

- **Design responsive** adaptatif
- **Touch-friendly** pour tablettes
- **Navigation optimisée** mobile
- **Performance** optimisée

## 🔒 Sécurité

- **Hashage des mots de passe** avec Werkzeug
- **Protection CSRF** avec Flask-WTF
- **Sessions sécurisées** avec tokens
- **Validation des données** côté serveur

## 📊 Analytics et Logs

- **Tracking des prédictions** utilisateur
- **Logs de performance** IA
- **Métriques d'utilisation** en temps réel
- **Rapports de précision** automatiques

## 🚀 Performance

- **Cache intelligent** Redis/Mémoire
- **Requêtes optimisées** avec SQLAlchemy
- **Compression** des réponses
- **Lazy loading** des graphiques

## 🔄 Mise à Jour

L'application se met à jour automatiquement :
- **Données des matchs** : Toutes les 5 secondes
- **Cache** : Invalidation intelligente
- **Sessions** : Nettoyage automatique

## 🐛 Dépannage

### Problèmes Courants

1. **Erreur de dépendances**
   ```bash
   python install_dependencies.py
   ```

2. **Base de données corrompue**
   ```bash
   rm sports_betting.db
   python fifa1.py  # Recrée automatiquement
   ```

3. **Cache Redis indisponible**
   - L'application fonctionne avec cache mémoire
   - Pas d'impact sur les fonctionnalités

## 📞 Support

- **Issues GitHub** : Pour les bugs et suggestions
- **Documentation** : README.md complet
- **Logs** : Fichier predictions.log pour debug

## 🎯 Roadmap

- [ ] Application mobile native
- [ ] Machine Learning réel avec historique
- [ ] Notifications push
- [ ] API publique
- [ ] Intégration Telegram
- [ ] Mode hors-ligne

---

**Développé avec ❤️ pour les passionnés de sports et de technologie SOLITAIRE HACK**
