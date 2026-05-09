"""
Декораторы для проверки прав доступа и других функций.
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from app.constants import USER_ROLE_ADMIN, USER_ROLE_MODERATOR, ERROR_PERMISSION_DENIED


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != USER_ROLE_ADMIN:
            abort(403, description=ERROR_PERMISSION_DENIED)
        return f(*args, **kwargs)
    return decorated_function


def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role not in [USER_ROLE_ADMIN, USER_ROLE_MODERATOR]:
            abort(403, description=ERROR_PERMISSION_DENIED)
        return f(*args, **kwargs)
    return decorated_function


def task_owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import Task
        task_id = kwargs.get('task_id')
        if not task_id:
            abort(400)
        task = Task.query.get_or_404(task_id)
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role in [USER_ROLE_ADMIN, USER_ROLE_MODERATOR]:
            return f(*args, **kwargs)
        if task.user_id != current_user.id:
            abort(403, description=ERROR_PERMISSION_DENIED)
        return f(*args, **kwargs)
    return decorated_function


def comment_owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import Comment
        comment_id = kwargs.get('comment_id')
        if not comment_id:
            abort(400)
        comment = Comment.query.get_or_404(comment_id)
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role in [USER_ROLE_ADMIN, USER_ROLE_MODERATOR]:
            return f(*args, **kwargs)
        if comment.user_id != current_user.id:
            abort(403, description=ERROR_PERMISSION_DENIED)
        return f(*args, **kwargs)
    return decorated_function


def log_action(action_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.models import UserActionLog
            from app import db
            from flask import request
            result = f(*args, **kwargs)
            if current_user.is_authenticated:
                log_entry = UserActionLog(
                    user_id=current_user.id,
                    action_type=action_type,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                db.session.add(log_entry)
                db.session.commit()
            return result
        return decorated_function
    return decorator


def rate_limit(max_requests=10, window_seconds=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session, request
            import time
            if not current_user.is_authenticated:
                return f(*args, **kwargs)
            key = f"rate_limit_{current_user.id}_{request.endpoint}"
            now = time.time()
            requests_data = session.get(key, [])
            requests_data = [t for t in requests_data if now - t < window_seconds]
            if len(requests_data) >= max_requests:
                abort(429, description=f'Превышен лимит запросов. Попробуйте через {window_seconds} секунд.')
            requests_data.append(now)
            session[key] = requests_data
            return f(*args, **kwargs)
        return decorated_function
    return decorator