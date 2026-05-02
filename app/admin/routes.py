from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.models import User, Task, Comment, UserActionLog
from app.forms import AdminUserEditForm, AdminTaskModerateForm
from app.decorators import admin_required, moderator_required
from app.constants import TASK_STATUSES
from datetime import datetime


@bp.route('/')
@login_required
@moderator_required
def dashboard():
    total_users = User.query.count()
    total_tasks = Task.query.count()
    total_comments = Comment.query.count()
    active_tasks = Task.query.filter_by(status='active').count()
    pending_tasks = Task.query.filter_by(status='pending').count()
    new_users_today = User.query.filter(User.created_at >= datetime.utcnow().date()).count()
    new_tasks_today = Task.query.filter(Task.created_at >= datetime.utcnow().date()).count()
    recent_logs = UserActionLog.query.order_by(UserActionLog.created_at.desc()).limit(20).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', total_users=total_users, total_tasks=total_tasks,
                           total_comments=total_comments, active_tasks=active_tasks, pending_tasks=pending_tasks,
                           new_users_today=new_users_today, new_tasks_today=new_tasks_today, recent_logs=recent_logs,
                           recent_users=recent_users, recent_tasks=recent_tasks)


@bp.route('/users')
@login_required
@admin_required
def users_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    query = User.query
    if search:
        query = query.filter(User.username.contains(search) | User.name.contains(search) | User.email.contains(search))
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=current_app.config['USERS_PER_PAGE'], error_out=False)
    users = pagination.items
    return render_template('admin/users.html', users=users, pagination=pagination, search=search)


@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserEditForm(original_username=user.username, obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.name = form.name.data
        user.email = form.email.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        user.reputation = form.reputation.data
        db.session.commit()
        flash('Пользователь обновлён', 'success')
        return redirect(url_for('admin.users_list'))
    return render_template('admin/user_edit.html', form=form, user=user)


@bp.route('/users/<int:user_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Нельзя заблокировать самого себя'}), 400
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': user.is_active})


@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Нельзя удалить самого себя', 'danger')
        return redirect(url_for('admin.users_list'))
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удалён', 'success')
    return redirect(url_for('admin.users_list'))


@bp.route('/tasks')
@login_required
@moderator_required
def tasks_list():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('q', '')
    query = Task.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search:
        query = query.filter(Task.title.contains(search))
    pagination = query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=current_app.config['TASKS_PER_PAGE'], error_out=False)
    tasks = pagination.items
    return render_template('admin/tasks.html', tasks=tasks, pagination=pagination, statuses=TASK_STATUSES,
                           current_status=status_filter, search=search)


@bp.route('/tasks/<int:task_id>/moderate', methods=['GET', 'POST'])
@login_required
@moderator_required
def moderate_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = AdminTaskModerateForm(obj=task)
    if form.validate_on_submit():
        task.status = form.status.data
        db.session.commit()
        flash('Статус задачи обновлён', 'success')
        return redirect(url_for('admin.tasks_list'))
    return render_template('admin/task_moderate.html', form=form, task=task)


@bp.route('/comments')
@login_required
@moderator_required
def comments_list():
    page = request.args.get('page', 1, type=int)
    query = Comment.query.order_by(Comment.created_at.desc())
    pagination = query.paginate(page=page, per_page=current_app.config['COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('admin/comments.html', comments=comments, pagination=pagination)


@bp.route('/comments/<int:comment_id>/toggle_status', methods=['POST'])
@login_required
@moderator_required
def toggle_comment_status(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.status = 'hidden' if comment.status == 'active' else 'active'
    db.session.commit()
    return jsonify({'success': True, 'status': comment.status})


@bp.route('/logs')
@login_required
@admin_required
def view_logs():
    page = request.args.get('page', 1, type=int)
    user_id = request.args.get('user_id', type=int)
    action_type = request.args.get('action_type', '')
    query = UserActionLog.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action_type:
        query = query.filter_by(action_type=action_type)
    pagination = query.order_by(UserActionLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    logs = pagination.items
    return render_template('admin/logs.html', logs=logs, pagination=pagination, user_id=user_id, action_type=action_type)