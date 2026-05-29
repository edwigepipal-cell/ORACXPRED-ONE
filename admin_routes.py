"""
🔐 ROUTES ADMINISTRATEUR ORACXPRED
==================================
Gestion complète de l'administration : utilisateurs, plans, prédictions, notifications
"""

from flask import Blueprint, request, render_template_string, session, redirect, url_for, jsonify, send_from_directory, current_app, Response
from datetime import datetime, timedelta
import json
import os
from functools import wraps

from models import (
    db, User, Prediction, SystemLog, SubscriptionPlan, UserSubscription,
    UserPredictionAccess, Notification, PersistentSession, BackupLog,
    PredictionSchedule, Alert, CollectedMatch, MatchCollectionLog
)
from oracxpred_utils import (
    save_profile_photo, delete_profile_photo, create_persistent_session,
    get_user_from_session_token, create_backup, cleanup_expired_sessions,
    ensure_user_unique_id, check_and_expire_subscriptions
)
from prediction_manager import log_action

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ========== FONCTIONS DE TEMPLATES (DOIT ÊTRE AVANT LES ROUTES) ==========

def get_admin_template(name):
    """Récupère un template admin depuis fifa1.py"""
    try:
        from fifa1 import (
            ADMIN_LOGIN_TEMPLATE, ADMIN_DASHBOARD_TEMPLATE
        )
        templates = {
            'login': ADMIN_LOGIN_TEMPLATE,
            'dashboard': ADMIN_DASHBOARD_TEMPLATE,
        }
        template = templates.get(name)
        if template and not template.startswith('<!--'):
            return template
    except (ImportError, AttributeError) as e:
        print(f"⚠️ Erreur lors du chargement du template {name}: {e}")
    
    # Retourner un template simple par défaut
    return get_simple_admin_template(name)


def get_simple_admin_template(name, **kwargs):
    """Retourne un template simple par défaut"""
    if name == 'login':
        return """<!DOCTYPE html>
<html><head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Connexion Admin - ORACXPRED</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container { 
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 50px;
            max-width: 450px;
            width: 100%;
        }
        h2 { text-align: center; color: #333; margin-bottom: 30px; font-size: 28px; }
        .form-group { margin-bottom: 25px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: 600; }
        input { width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 16px; }
        input:focus { outline: none; border-color: #667eea; }
        .btn { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: 600; cursor: pointer; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4); }
        .error { background: #fee; color: #c33; padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .links { text-align: center; margin-top: 25px; padding-top: 25px; border-top: 1px solid #e0e0e0; }
        .links a { color: #667eea; text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 Connexion Admin</h2>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <div class="form-group">
                <label for="username">Nom d'utilisateur :</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Mot de passe :</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Se connecter</button>
        </form>
        <div class="links">
            <a href="/">← Retour à l'accueil</a>
        </div>
    </div>
</body>
</html>"""
    elif name == 'users':
        return """<!DOCTYPE html>
<html><head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Utilisateurs - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f7fb; padding: 20px; }
        .bar { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
        .pill { display: inline-block; padding: 8px 14px; border-radius: 999px; background: #eef2ff; color: #3f3f8f; font-weight: 700; font-size: 13px; }
        .actions { display: flex; gap: 10px; flex-wrap: wrap; }
        .actions a { text-decoration: none; background: #667eea; color: white; padding: 10px 14px; border-radius: 10px; font-weight: 600; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }
        th, td { padding: 12px 14px; border-bottom: 1px solid #eee; text-align: left; }
        th { background: #667eea; color: white; }
    </style>
</head>
<body>
    <div class="bar">
        <div>
            <h1>Gestion des Utilisateurs</h1>
            <div class="pill">Base active: {{ database_backend }} | Source: {{ database_source }}</div>
        </div>
        <div class="actions">
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/users/export">Export CSV</a>
        </div>
    </div>
    <table>
        <tr><th>ID</th><th>Username</th><th>Email</th><th>Admin</th><th>Approuvé</th></tr>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email or '-' }}</td>
            <td>{{ 'Oui' if user.is_admin else 'Non' }}</td>
            <td>{{ 'Oui' if user.is_approved else 'Non' }}</td>
        </tr>
        {% endfor %}
    </table>
</body></html>"""
    elif name == 'plans':
        return """<!DOCTYPE html>
<html><head><title>Plans - Admin</title></head>
<body>
    <h1>Gestion des Plans</h1>
    <p>Page en cours de développement...</p>
</body></html>"""
    elif name == 'predictions':
        return """<!DOCTYPE html>
<html><head><title>Prédictions - Admin</title></head>
<body>
    <h1>Gestion des Prédictions</h1>
    <p>Page en cours de développement...</p>
</body></html>"""
    elif name == 'notifications':
        return """<!DOCTYPE html>
<html><head><title>Notifications - Admin</title></head>
<body>
    <h1>Gestion des Notifications</h1>
    <p>Page en cours de développement...</p>
</body></html>"""
    elif name == 'backups':
        return """<!DOCTYPE html>
<html><head><title>Sauvegardes - Admin</title></head>
<body>
    <h1>Gestion des Sauvegardes</h1>
    <p>Page en cours de développement...</p>
</body></html>"""
    
    return f"<html><body><h1>Template {name} non disponible</h1></body></html>"


def require_admin(f):
    """Décorateur pour exiger les droits admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Compatibilité avec l'ancien système
        admin_logged_in = session.get('admin_logged_in')
        admin_id = session.get('admin_id')
        user_id = session.get('user_id')
        
        # Vérifier via l'ancien système ou le nouveau
        if admin_logged_in and admin_id:
            try:
                user = User.query.get(admin_id)
                if user and user.is_admin and user.is_active:
                    return f(*args, **kwargs)
            except Exception as e:
                print(f"❌ Erreur lors de la vérification admin: {e}")
        
        if user_id:
            try:
                user = User.query.get(user_id)
                if user and user.is_admin and user.is_active:
                    return f(*args, **kwargs)
            except Exception as e:
                print(f"❌ Erreur lors de la vérification admin: {e}")
        
        return redirect(url_for('admin.admin_login'))
    return decorated_function


def _get_database_backend_label():
    """Retourne un libellé lisible de la base active pour l'admin."""
    uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("postgresql://") or uri.startswith("postgres://"):
        if "supabase" in uri:
            return "Supabase PostgreSQL"
        return "PostgreSQL"
    if uri.startswith("sqlite:///"):
        return "SQLite locale"
    return "Base distante"


def _get_database_connection_source():
    """Indique quelle variable d'environnement alimente la base active."""
    for env_name in ("SUPABASE_DATABASE_URL", "SUPABASE_POOLER_URL", "SUPABASE_POSTGRES_URL", "DATABASE_URL"):
        if os.getenv(env_name, "").strip():
            return env_name
    return "fallback local"


@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Connexion admin masquée: redirige vers le login utilisateur standard."""
    return redirect(url_for('user.user_login'))


@admin_bp.route('/logout')
def admin_logout():
    """Déconnexion admin"""
    user = User.query.get(session.get('user_id'))
    if user:
        log_action('admin_logout', f"Déconnexion admin: {user.username}", user_id=user.id, severity='info')
    
    # Supprimer la session persistante si elle existe
    token = session.get('persistent_token')
    if token:
        delete_persistent_session(token)
    
    session.clear()
    return redirect(url_for('admin.admin_login'))


@admin_bp.route('/dashboard')
@require_admin
def admin_dashboard():
    """Tableau de bord admin principal"""
    admin_user = User.query.get(session.get('user_id'))
    
    # Statistiques
    total_users = User.query.count()
    active_subscriptions = UserSubscription.query.filter(
        UserSubscription.is_active == True,
        UserSubscription.expires_at > datetime.utcnow()
    ).count()
    pending_approvals = User.query.filter_by(is_approved=False).count()
    total_predictions = Prediction.query.count()
    active_predictions = Prediction.query.filter_by(is_valid=True, is_locked=False).count()
    
    # Abonnements expirés récemment
    recently_expired = UserSubscription.query.filter(
        UserSubscription.is_active == False,
        UserSubscription.expires_at > datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Notifications non lues
    unread_notifications = Notification.query.filter_by(is_read=False).count()
    
    # Logs récents
    recent_logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(20).all()
    
    try:
        template = get_admin_template('dashboard')
        return render_template_string(template,
            admin_user=admin_user,
            total_users=total_users,
            active_subscriptions=active_subscriptions,
            pending_approvals=pending_approvals,
            total_predictions=total_predictions,
            active_predictions=active_predictions,
            recently_expired=recently_expired,
            unread_notifications=unread_notifications,
            recent_logs=recent_logs,
            database_backend=_get_database_backend_label(),
            database_source=_get_database_connection_source(),
        )
    except Exception as e:
        print(f"❌ Erreur lors du rendu du dashboard: {e}")
        import traceback
        traceback.print_exc()
        return f"""
        <html>
        <head><title>Erreur Dashboard</title></head>
        <body>
            <h1>Erreur lors du chargement du dashboard</h1>
            <p>Erreur: {str(e)}</p>
            <p>Admin User: {admin_user.username if admin_user else 'None'}</p>
            <p>Total Users: {total_users}</p>
        </body>
        </html>
        """


# ========== GESTION DES UTILISATEURS ==========

@admin_bp.route('/users')
@require_admin
def admin_users():
    """Liste des utilisateurs"""
    users = User.query.order_by(User.created_at.desc()).all()
    template = get_admin_template('users')
    return render_template_string(
        template,
        users=users,
        database_backend=_get_database_backend_label(),
        database_source=_get_database_connection_source(),
    )


@admin_bp.route('/users/export')
@require_admin
def admin_export_users():
    """Exporte les utilisateurs en CSV."""
    import csv
    from io import StringIO

    users = User.query.order_by(User.created_at.desc()).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'id', 'username', 'email', 'is_admin', 'is_approved', 'is_active',
        'subscription_plan', 'subscription_status', 'subscription_expires_at',
        'created_at', 'last_login_at'
    ])
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email or '',
            int(bool(user.is_admin)),
            int(bool(user.is_approved)),
            int(bool(user.is_active)),
            user.subscription_plan or '',
            user.subscription_status or '',
            user.subscription_expires_at.isoformat() if user.subscription_expires_at else '',
            user.created_at.isoformat() if user.created_at else '',
            user.last_login_at.isoformat() if user.last_login_at else ''
        ])

    output.seek(0)
    filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@admin_bp.route('/user/<int:user_id>/toggle_active', methods=['POST'])
@require_admin
def admin_toggle_user_active(user_id):
    """Activer/désactiver un utilisateur"""
    admin_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    
    if user.is_admin and user.id != admin_id:
        return jsonify({'error': 'Impossible de désactiver un autre admin'}), 403
    
    user.is_active = not user.is_active
    db.session.commit()
    
    action = 'activé' if user.is_active else 'désactivé'
    log_action('admin_action', f"Utilisateur {user.username} {action}", 
               user_id=user_id, admin_id=admin_id, severity='info')
    
    return jsonify({'success': True, 'is_active': user.is_active})


@admin_bp.route('/user/<int:user_id>/approve', methods=['POST'])
@require_admin
def admin_approve_user(user_id):
    """Approuver un utilisateur"""
    admin_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    
    user.is_approved = True
    ensure_user_unique_id(user)  # Assurer l'ID unique
    db.session.commit()
    
    log_action('admin_action', f"Utilisateur {user.username} approuvé", 
               user_id=user_id, admin_id=admin_id, severity='info')
    
    return jsonify({'success': True})


@admin_bp.route('/user/<int:user_id>/set_subscription', methods=['POST'])
@require_admin
def admin_set_subscription(user_id):
    """Attribuer un abonnement à un utilisateur"""
    admin_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    
    plan_id = request.json.get('plan_id')
    if not plan_id:
        return jsonify({'error': 'Plan ID requis'}), 400
    
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan or not plan.is_active:
        return jsonify({'error': 'Plan invalide'}), 400
    
    # Désactiver les anciens abonnements actifs
    old_subscriptions = UserSubscription.query.filter_by(
        user_id=user_id,
        is_active=True
    ).all()
    for sub in old_subscriptions:
        sub.is_active = False
    
    # Créer le nouvel abonnement
    start_date = datetime.utcnow()
    expires_at = start_date + timedelta(days=plan.duration_days)
    
    subscription = UserSubscription(
        user_id=user_id,
        plan_id=plan_id,
        start_date=start_date,
        expires_at=expires_at,
        is_active=True
    )
    db.session.add(subscription)
    db.session.commit()
    
    log_action('admin_action', f"Abonnement {plan.name} attribué à {user.username}", 
               user_id=user_id, admin_id=admin_id, severity='info')
    
    return jsonify({'success': True, 'expires_at': expires_at.isoformat()})


# ========== GESTION DES PLANS TARIFAIRES ==========

@admin_bp.route('/plans')
@require_admin
def admin_plans():
    """Gestion des plans tarifaires"""
    plans = SubscriptionPlan.query.order_by(SubscriptionPlan.created_at.desc()).all()
    template = get_admin_template('plans')
    return render_template_string(template, plans=plans)


@admin_bp.route('/plan/create', methods=['POST'])
@require_admin
def admin_create_plan():
    """Créer un nouveau plan tarifaire"""
    admin_id = session.get('user_id')
    
    name = request.json.get('name', '').strip()
    description = request.json.get('description', '').strip()
    predictions_per_day = int(request.json.get('predictions_per_day', 3))
    duration_days = int(request.json.get('duration_days', 7))
    duration_type = request.json.get('duration_type', 'week')
    price_fcfa = float(request.json.get('price_fcfa', 0))
    
    if not name or price_fcfa <= 0:
        return jsonify({'error': 'Données invalides'}), 400
    
    # Vérifier si le nom existe déjà
    if SubscriptionPlan.query.filter_by(name=name).first():
        return jsonify({'error': 'Un plan avec ce nom existe déjà'}), 400
    
    plan = SubscriptionPlan(
        name=name,
        description=description,
        predictions_per_day=predictions_per_day,
        duration_days=duration_days,
        duration_type=duration_type,
        price_fcfa=price_fcfa,
        is_active=True,
        created_by=admin_id
    )
    db.session.add(plan)
    db.session.commit()
    
    log_action('admin_action', f"Plan créé: {name}", admin_id=admin_id, severity='info')
    
    return jsonify({'success': True, 'plan_id': plan.id})


@admin_bp.route('/plan/<int:plan_id>/update', methods=['POST'])
@require_admin
def admin_update_plan(plan_id):
    """Modifier un plan tarifaire"""
    admin_id = session.get('user_id')
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    
    plan.name = request.json.get('name', plan.name).strip()
    plan.description = request.json.get('description', plan.description).strip()
    plan.predictions_per_day = int(request.json.get('predictions_per_day', plan.predictions_per_day))
    plan.duration_days = int(request.json.get('duration_days', plan.duration_days))
    plan.duration_type = request.json.get('duration_type', plan.duration_type)
    plan.price_fcfa = float(request.json.get('price_fcfa', plan.price_fcfa))
    plan.is_active = request.json.get('is_active', plan.is_active)
    
    db.session.commit()
    
    log_action('admin_action', f"Plan modifié: {plan.name}", admin_id=admin_id, severity='info')
    
    return jsonify({'success': True})


@admin_bp.route('/plan/<int:plan_id>/delete', methods=['POST'])
@require_admin
def admin_delete_plan(plan_id):
    """Supprimer un plan tarifaire"""
    admin_id = session.get('user_id')
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    
    # Vérifier s'il y a des abonnements actifs
    active_subs = UserSubscription.query.filter_by(plan_id=plan_id, is_active=True).count()
    if active_subs > 0:
        return jsonify({'error': f'Impossible de supprimer: {active_subs} abonnements actifs'}), 400
    
    plan.is_active = False
    db.session.commit()
    
    log_action('admin_action', f"Plan désactivé: {plan.name}", admin_id=admin_id, severity='info')
    
    return jsonify({'success': True})


# ========== GESTION DES PRÉDICTIONS ==========

@admin_bp.route('/predictions')
@require_admin
def admin_predictions():
    """Gestion des prédictions"""
    predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(100).all()
    schedule = PredictionSchedule.query.filter_by(is_active=True).first()
    
    template = get_admin_template('predictions')
    return render_template_string(template,
        predictions=predictions,
        schedule=schedule
    )


@admin_bp.route('/predictions/schedule', methods=['POST'])
@require_admin
def admin_set_prediction_schedule():
    """Configurer le planning des prédictions"""
    admin_id = session.get('user_id')
    
    predictions_per_day = int(request.json.get('predictions_per_day', 3))
    publication_times = request.json.get('publication_times', [])
    publication_delays = request.json.get('publication_delays', [])
    
    # Désactiver l'ancien planning
    old_schedules = PredictionSchedule.query.filter_by(is_active=True).all()
    for sched in old_schedules:
        sched.is_active = False
    
    # Créer le nouveau planning
    schedule = PredictionSchedule(
        predictions_per_day=predictions_per_day,
        publication_times=json.dumps(publication_times),
        publication_delays=json.dumps(publication_delays),
        is_active=True,
        created_by=admin_id
    )
    db.session.add(schedule)
    db.session.commit()
    
    log_action('admin_action', f"Planning prédictions configuré: {predictions_per_day}/jour", 
               admin_id=admin_id, severity='info')
    
    return jsonify({'success': True})


@admin_bp.route('/prediction/<int:prediction_id>/invalidate', methods=['POST'])
@require_admin
def admin_invalidate_prediction(prediction_id):
    """Invalider une prédiction"""
    admin_id = session.get('user_id')
    prediction = Prediction.query.get_or_404(prediction_id)
    
    prediction.is_valid = False
    prediction.invalidated_by = admin_id
    prediction.invalidated_at = datetime.utcnow()
    db.session.commit()
    
    log_action('admin_action', f"Prédiction {prediction_id} invalidée", 
               admin_id=admin_id, severity='warning')
    
    return jsonify({'success': True})


# ========== GESTION DES NOTIFICATIONS ==========

@admin_bp.route('/notifications')
@require_admin
def admin_notifications():
    """Gestion des notifications"""
    notifications = Notification.query.order_by(Notification.created_at.desc()).limit(100).all()
    template = get_admin_template('notifications')
    return render_template_string(template, notifications=notifications)


@admin_bp.route('/notification/create', methods=['POST'])
@require_admin
def admin_create_notification():
    """Créer une notification"""
    admin_id = session.get('user_id')
    
    title = request.json.get('title', '').strip()
    message = request.json.get('message', '').strip()
    priority = request.json.get('priority', 'normal')
    notification_type = request.json.get('type', 'info')
    display_duration = int(request.json.get('display_duration', 5000))
    is_global = request.json.get('is_global', True)
    user_id = request.json.get('user_id') if not is_global else None
    
    if not title or not message:
        return jsonify({'error': 'Titre et message requis'}), 400
    
    # Si notification globale, créer pour tous les utilisateurs
    if is_global:
        users = User.query.filter_by(is_approved=True, is_active=True).all()
        for user in users:
            notification = Notification(
                user_id=user.id,
                is_global=True,
                title=title,
                message=message,
                priority=priority,
                notification_type=notification_type,
                display_duration=display_duration,
                created_by=admin_id
            )
            db.session.add(notification)
    else:
        if not user_id:
            return jsonify({'error': 'user_id requis pour notification ciblée'}), 400
        notification = Notification(
            user_id=user_id,
            is_global=False,
            title=title,
            message=message,
            priority=priority,
            notification_type=notification_type,
            display_duration=display_duration,
            created_by=admin_id
        )
        db.session.add(notification)
    
    db.session.commit()
    
    log_action('admin_action', f"Notification créée: {title}", admin_id=admin_id, severity='info')
    
    return jsonify({'success': True})


# ========== SAUVEGARDES ==========

@admin_bp.route('/backup/create', methods=['POST'])
@require_admin
def admin_create_backup():
    """Créer une sauvegarde manuelle"""
    admin_id = session.get('user_id')
    backup_path = create_backup('manual', admin_id)
    
    if backup_path:
        log_action('admin_action', f"Sauvegarde créée: {backup_path}", admin_id=admin_id, severity='info')
        return jsonify({'success': True, 'backup_path': backup_path})
    else:
        return jsonify({'error': 'Échec de la sauvegarde'}), 500


@admin_bp.route('/backups')
@require_admin
def admin_backups():
    """Liste des sauvegardes"""
    backups = BackupLog.query.order_by(BackupLog.created_at.desc()).limit(50).all()
    template = get_admin_template('backups')
    return render_template_string(template, backups=backups)


# ========== TASKS AUTOMATIQUES ==========

@admin_bp.route('/tasks/cleanup', methods=['POST'])
@require_admin
def admin_run_cleanup():
    """Exécuter les tâches de nettoyage"""
    admin_id = session.get('user_id')
    
    expired_sessions = cleanup_expired_sessions()
    expired_subscriptions = check_and_expire_subscriptions()
    
    log_action('admin_action', 
               f"Nettoyage: {expired_sessions} sessions, {expired_subscriptions} abonnements", 
               admin_id=admin_id, severity='info')
    
    return jsonify({
        'success': True,
        'expired_sessions': expired_sessions,
        'expired_subscriptions': expired_subscriptions
    })


# ========== ROUTES POUR LA GESTION DES MATCHS COLLECTÉS ==========

@admin_bp.route('/matchs-collectes')
@require_admin
def admin_matchs_collectes():
    """Page admin des matchs collectés avec gestion complète"""
    
    # Récupérer les paramètres
    page = request.args.get('page', 1, type=int)
    per_page = 50
    jeu_filter = request.args.get('jeu', 'all')
    statut_filter = request.args.get('statut', 'all')
    source_filter = request.args.get('source', 'all')
    
    # Construire la requête
    query = CollectedMatch.query
    
    # Appliquer les filtres
    if jeu_filter != 'all':
        query = query.filter(CollectedMatch.jeu == jeu_filter)
    
    if statut_filter != 'all':
        query = query.filter(CollectedMatch.statut == statut_filter)
    
    if source_filter != 'all':
        query = query.filter(CollectedMatch.source_donnees == source_filter)
    
    # Ordre et pagination
    matches_pagination = query.order_by(CollectedMatch.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    matches = matches_pagination.items
    
    # Statistiques détaillées
    stats = {
        'total_matches': CollectedMatch.query.count(),
        'by_status': {},
        'by_game': {},
        'by_source': {},
        'last_24h': CollectedMatch.query.filter(
            CollectedMatch.created_at >= datetime.now() - timedelta(hours=24)
        ).count(),
        'last_7d': CollectedMatch.query.filter(
            CollectedMatch.created_at >= datetime.now() - timedelta(days=7)
        ).count()
    }
    
    # Statuts
    for status in ['en_attente', 'en_cours', 'termine', 'annule']:
        stats['by_status'][status] = CollectedMatch.query.filter_by(statut=status).count()
    
    # Jeux
    for game in ['FIFA', 'eFootball', 'FC']:
        stats['by_game'][game] = CollectedMatch.query.filter_by(jeu=game).count()
    
    # Sources
    sources = db.session.query(CollectedMatch.source_donnees, db.func.count(CollectedMatch.id)).group_by(CollectedMatch.source_donnees).all()
    for source, count in sources:
        stats['by_source'][source or 'unknown'] = count
    
    # Logs récents du système
    recent_logs = MatchCollectionLog.query.order_by(MatchCollectionLog.created_at.desc()).limit(20).all()
    
    template = '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Matchs Collectés - Admin ORACXPRED</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { opacity: 0.9; font-size: 1.1em; }
            .nav-bar { background: white; padding: 15px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .nav-bar a { color: #667eea; text-decoration: none; margin-right: 20px; padding: 8px 16px; border-radius: 5px; transition: all 0.3s; }
            .nav-bar a:hover { background: #667eea; color: white; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; }
            .stat-number { font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 10px; }
            .stat-label { color: #666; font-weight: 500; }
            .filters { background: white; padding: 25px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
            .filter-row { display: flex; gap: 20px; flex-wrap: wrap; align-items: end; margin-bottom: 20px; }
            .filter-group { display: flex; flex-direction: column; min-width: 150px; }
            .filter-group label { font-weight: bold; margin-bottom: 8px; color: #333; }
            .filter-group select { padding: 10px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; background: white; }
            .btn { padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; transition: all 0.3s; }
            .btn-primary { background: #667eea; color: white; }
            .btn-primary:hover { background: #5a6fd8; }
            .btn-success { background: #28a745; color: white; }
            .btn-warning { background: #ffc107; color: #212529; }
            .btn-danger { background: #dc3545; color: white; }
            .matches-table { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 30px; }
            .table { width: 100%; border-collapse: collapse; }
            .table th { background: #667eea; color: white; padding: 15px; text-align: left; font-weight: 600; }
            .table td { padding: 15px; border-bottom: 1px solid #eee; }
            .table tr:hover { background: #f8f9fa; }
            .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; text-transform: uppercase; }
            .status-en_attente { background: #fff3cd; color: #856404; }
            .status-en_cours { background: #cce5ff; color: #004085; }
            .status-termine { background: #d4edda; color: #155724; }
            .status-annule { background: #f8d7da; color: #721c24; }
            .game-badge { padding: 4px 12px; border-radius: 15px; font-size: 0.8em; font-weight: bold; background: #667eea; color: white; }
            .pagination { display: flex; justify-content: center; gap: 10px; margin: 30px 0; }
            .pagination a { padding: 10px 15px; background: white; color: #667eea; text-decoration: none; border-radius: 8px; border: 1px solid #ddd; transition: all 0.3s; }
            .pagination a:hover { background: #667eea; color: white; border-color: #667eea; }
            .pagination .current { background: #667eea; color: white; border-color: #667eea; }
            .logs-section { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
            .log-item { padding: 15px; border-left: 4px solid #667eea; margin-bottom: 15px; background: rgba(102,126,234,0.05); border-radius: 0 8px 8px 0; }
            .log-time { font-size: 0.9em; color: #666; margin-bottom: 5px; }
            .log-message { color: #333; font-weight: 500; }
            .log-severity { padding: 2px 8px; border-radius: 12px; font-size: 0.7em; font-weight: bold; text-transform: uppercase; }
            .severity-info { background: #e3f2fd; color: #1976d2; }
            .severity-warning { background: #fff3e0; color: #f57c00; }
            .severity-error { background: #ffebee; color: #d32f2f; }
            .actions { display: flex; gap: 10px; }
            .btn-sm { padding: 6px 12px; font-size: 0.8em; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎮 Matchs Collectés - Admin</h1>
                <p>Gestion complète du système de collecte ORACXPRED</p>
            </div>
            
            <div class="nav-bar">
                <a href="/admin/dashboard">🏠 Dashboard</a>
                <a href="/admin/matchs-collectes">🎮 Matchs Collectés</a>
                <a href="/admin/users">👥 Utilisateurs</a>
                <a href="/admin/predictions">🔮 Prédictions</a>
                <a href="/admin/logs">📊 Logs</a>
                <a href="/admin/settings">⚙️ Paramètres</a>
                <a href="/logout" style="margin-left: auto; background: #dc3545; color: white;">🚪 Déconnexion</a>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{{ stats.total_matches }}</div>
                    <div class="stat-label">Total Matchs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.last_24h }}</div>
                    <div class="stat-label">Dernières 24h</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.last_7d }}</div>
                    <div class="stat-label">Derniers 7 jours</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.by_status.en_cours }}</div>
                    <div class="stat-label">En Cours</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.by_status.termine }}</div>
                    <div class="stat-label">Terminés</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ stats.by_game.FIFA }}</div>
                    <div class="stat-label">FIFA</div>
                </div>
            </div>
            
            <div class="filters">
                <form method="GET">
                    <div class="filter-row">
                        <div class="filter-group">
                            <label>Jeu</label>
                            <select name="jeu">
                                <option value="all" {% if jeu_filter == 'all' %}selected{% endif %}>Tous</option>
                                <option value="FIFA" {% if jeu_filter == 'FIFA' %}selected{% endif %}>FIFA</option>
                                <option value="eFootball" {% if jeu_filter == 'eFootball' %}selected{% endif %}>eFootball</option>
                                <option value="FC" {% if jeu_filter == 'FC' %}selected{% endif %}>FC</option>
                            </select>
                        </div>
                        <div class="filter-group">
                            <label>Statut</label>
                            <select name="statut">
                                <option value="all" {% if statut_filter == 'all' %}selected{% endif %}>Tous</option>
                                <option value="en_attente" {% if statut_filter == 'en_attente' %}selected{% endif %}>En attente</option>
                                <option value="en_cours" {% if statut_filter == 'en_cours' %}selected{% endif %}>En cours</option>
                                <option value="termine" {% if statut_filter == 'termine' %}selected{% endif %}>Terminé</option>
                                <option value="annule" {% if statut_filter == 'annule' %}selected{% endif %}>Annulé</option>
                            </select>
                        </div>
                        <div class="filter-group">
                            <label>Source</label>
                            <select name="source">
                                <option value="all" {% if source_filter == 'all' %}selected{% endif %}>Toutes</option>
                                {% for source in stats.by_source.keys() %}
                                <option value="{{ source }}" {% if source_filter == source %}selected{% endif %}>{{ source }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="filter-group">
                            <label>&nbsp;</label>
                            <button type="submit" class="btn btn-primary">Appliquer</button>
                        </div>
                        <div class="filter-group">
                            <label>&nbsp;</label>
                            <button type="button" class="btn btn-success" onclick="location.reload()">🔄 Actualiser</button>
                        </div>
                    </div>
                </form>
            </div>
            
            <div class="matches-table">
                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Match</th>
                            <th>Jeu</th>
                            <th>Score</th>
                            <th>Statut</th>
                            <th>Début</th>
                            <th>Source</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for match in matches %}
                        <tr>
                            <td><code>{{ match.unique_match_id[:8] }}...</code></td>
                            <td>
                                <strong>{{ match.equipe_domicile }}</strong><br>
                                <small>vs {{ match.equipe_exterieur }}</small>
                            </td>
                            <td><span class="game-badge">{{ match.jeu }}</span></td>
                            <td>
                                {% if match.score_domicile is not none %}
                                <strong>{{ match.score_domicile }} - {{ match.score_exterieur }}</strong>
                                {% if match.equipe_gagnante %}
                                <br><small>{{ match.equipe_gagnante }}</small>
                                {% endif %}
                                {% else %}
                                <em>-</em>
                                {% endif %}
                            </td>
                            <td><span class="status-badge status-{{ match.statut }}">{{ match.statut.replace('_', ' ') }}</span></td>
                            <td>{{ match.heure_debut.strftime('%d/%m %H:%M') if match.heure_debut else 'N/A' }}</td>
                            <td>{{ match.source_donnees or 'N/A' }}</td>
                            <td>
                                <div class="actions">
                                    <button class="btn btn-sm btn-primary" onclick="viewMatch({{ match.id }})">👁️</button>
                                    {% if match.statut == 'termine' %}
                                    <button class="btn btn-sm btn-success" onclick="validateMatch({{ match.id }})">✅</button>
                                    {% endif %}
                                    <button class="btn btn-sm btn-warning" onclick="editMatch({{ match.id }})">✏️</button>
                                    <button class="btn btn-sm btn-danger" onclick="deleteMatch({{ match.id }})">🗑️</button>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            {% if matches_pagination.pages > 1 %}
            <div class="pagination">
                {% if matches_pagination.has_prev %}
                <a href="?page={{ matches_pagination.prev_num }}&jeu={{ jeu_filter }}&statut={{ statut_filter }}&source={{ source_filter }}">«</a>
                {% endif %}
                
                {% for p in matches_pagination.iter_pages() %}
                    {% if p %}
                        {% if p == matches_pagination.page %}
                        <span class="current">{{ p }}</span>
                        {% else %}
                        <a href="?page={{ p }}&jeu={{ jeu_filter }}&statut={{ statut_filter }}&source={{ source_filter }}">{{ p }}</a>
                        {% endif %}
                    {% else %}
                    <span>...</span>
                    {% endif %}
                {% endfor %}
                
                {% if matches_pagination.has_next %}
                <a href="?page={{ matches_pagination.next_num }}&jeu={{ jeu_filter }}&statut={{ statut_filter }}&source={{ source_filter }}">»</a>
                {% endif %}
            </div>
            {% endif %}
            
            <div class="logs-section">
                <h3 style="margin-bottom: 20px; color: #333;">📊 Activité Récente du Système</h3>
                {% for log in recent_logs %}
                <div class="log-item">
                    <div class="log-time">{{ log.created_at.strftime('%d/%m/%Y %H:%M:%S') }}</div>
                    <div class="log-message">{{ log.message }}</div>
                    <span class="log-severity severity-{{ log.severity }}">{{ log.severity }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <script>
            function viewMatch(id) {
                // Implémenter la vue détaillée du match
                alert('Vue détaillée du match ID: ' + id);
            }
            
            function validateMatch(id) {
                if (confirm('Valider ce match terminé ?')) {
                    fetch('/admin/matchs-collectes/validate/' + id, {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Erreur: ' + data.error);
                        }
                    });
                }
            }
            
            function editMatch(id) {
                // Implémenter l'édition du match
                alert('Édition du match ID: ' + id);
            }
            
            function deleteMatch(id) {
                if (confirm('Supprimer ce match ? Cette action est irréversible.')) {
                    fetch('/admin/matchs-collectes/delete/' + id, {method: 'DELETE'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Erreur: ' + data.error);
                        }
                    });
                }
            }
        </script>
    </body>
    </html>
    '''
    
    return render_template_string(template, 
        matches=matches,
        matches_pagination=matches_pagination,
        stats=stats,
        recent_logs=recent_logs,
        jeu_filter=jeu_filter,
        statut_filter=statut_filter,
        source_filter=source_filter
    )


@admin_bp.route('/matchs-collectes/validate/<int:match_id>', methods=['POST'])
@require_admin
def admin_validate_match(match_id):
    """Valide un match terminé"""
    
    match = CollectedMatch.query.get_or_404(match_id)
    admin_id = session.get('user_id')
    
    if match.statut != 'termine':
        return jsonify({'error': 'Seuls les matchs terminés peuvent être validés'}), 400
    
    try:
        # Marquer comme validé (pourrait ajouter un champ is_validated)
        match.collecte_par = f"validated_by_admin_{admin_id}"
        db.session.commit()
        
        log_action('admin_action', f"Match validé: {match.unique_match_id}", admin_id=admin_id)
        
        return jsonify({'success': True, 'message': 'Match validé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/matchs-collectes/delete/<int:match_id>', methods=['DELETE'])
@require_admin
def admin_delete_match(match_id):
    """Supprime un match collecté"""
    
    match = CollectedMatch.query.get_or_404(match_id)
    admin_id = session.get('user_id')
    
    try:
        match_id_str = match.unique_match_id
        db.session.delete(match)
        db.session.commit()
        
        log_action('admin_action', f"Match supprimé: {match_id_str}", admin_id=admin_id, severity='warning')
        
        return jsonify({'success': True, 'message': 'Match supprimé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/matchs-collectes/export')
@require_admin
def admin_export_matches():
    """Exporte les matchs collectés en CSV"""
    
    import csv
    from io import StringIO
    from flask import Response
    
    matches = CollectedMatch.query.order_by(CollectedMatch.created_at.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # En-tête CSV
    writer.writerow([
        'ID', 'Jeu', 'Equipe Domicile', 'Equipe Exterieur', 
        'Score Domicile', 'Score Exterieur', 'Equipe Gagnante',
        'Statut', 'Heure Debut', 'Heure Fin', 'Source',
        'Date Creation'
    ])
    
    # Données
    for match in matches:
        writer.writerow([
            match.unique_match_id,
            match.jeu,
            match.equipe_domicile,
            match.equipe_exterieur,
            match.score_domicile or '',
            match.score_exterieur or '',
            match.equipe_gagnante or '',
            match.statut,
            match.heure_debut.isoformat() if match.heure_debut else '',
            match.heure_fin.isoformat() if match.heure_fin else '',
            match.source_donnees or '',
            match.created_at.isoformat() if match.created_at else ''
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=matchs_collectes_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'}
    )


@admin_bp.route('/matchs-collectes/stats')
@require_admin
def admin_matchs_stats():
    """API pour les statistiques détaillées des matchs collectés"""
    
    try:
        # Importer le collecteur pour les stats
        from match_collector import MatchCollector
        collector = MatchCollector("simulated", 30)
        stats = collector.get_statistics()
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Les fonctions sont maintenant définies au début du fichier

# Variables pour compatibilité
ADMIN_LOGIN_TEMPLATE = None
ADMIN_DASHBOARD_TEMPLATE = None
ADMIN_USERS_TEMPLATE = None
ADMIN_PLANS_TEMPLATE = None
ADMIN_PREDICTIONS_TEMPLATE = None
ADMIN_NOTIFICATIONS_TEMPLATE = None
ADMIN_BACKUPS_TEMPLATE = None
