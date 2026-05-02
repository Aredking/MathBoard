import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.profile import bp
from app.models import User, Task, Favorite, Statistics, Category, Comment
from app.forms import ProfileEditForm, ChangePasswordForm
from app.utils import save_uploaded_file
from app.constants import SUCCESS_PROFILE_UPDATED, SUCCESS_AVATAR_UPLOADED
from sqlalchemy import func
from datetime import date, timedelta


@bp.route('/<username>')
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    tasks_query = Task.query.filter_by(user_id=user.id, status='active').order_by(Task.created_at.desc())
    pagination = tasks_query.paginate(page=page, per_page=10, error_out=False)
    tasks = pagination.items
    stats = {
        'tasks_created': user.tasks_created,
        'tasks_solved': user.tasks_solved,
        'likes_received': user.total_likes_received,
        'reputation': user.reputation
    }
    return render_template('profile.html', title=f'Профиль {user.name}', user=user, tasks=tasks, pagination=pagination, stats=stats)


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileEditForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.website = form.website.data
        if form.avatar.data:
            filename = save_uploaded_file(form.avatar.data, subfolder='avatars')
            if filename:
                if current_user.avatar and current_user.avatar != 'default_avatar.png':
                    old_path = os.path.join(current_app.config['AVATAR_FOLDER'], current_user.avatar)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                current_user.avatar = filename
                flash(SUCCESS_AVATAR_UPLOADED, 'success')
        db.session.commit()
        flash(SUCCESS_PROFILE_UPDATED, 'success')
        return redirect(url_for('profile.view_profile', username=current_user.username))
    return render_template('profile_edit.html', title='Редактирование профиля', form=form)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменён!', 'success')
            return redirect(url_for('profile.view_profile', username=current_user.username))
        else:
            flash('Неверный текущий пароль', 'danger')
    return render_template('change_password.html', title='Смена пароля', form=form)


@bp.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', 1, type=int)
    favs = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc())
    pagination = favs.paginate(page=page, per_page=10, error_out=False)
    tasks = [fav.task for fav in pagination.items]
    return render_template('favorites.html', title='Избранное', tasks=tasks, pagination=pagination)


@bp.route('/statistics')
def statistics():
    total_users = User.query.count()
    total_tasks = Task.query.filter_by(status='active').count()
    total_solves = db.session.query(func.sum(Task.solves_count)).scalar() or 0
    total_comments = Comment.query.filter_by(status='active').count()
    top_users = User.query.order_by(User.reputation.desc()).limit(10).all()
    top_creators = User.query.order_by(User.tasks_created.desc()).limit(10).all()
    top_solvers = User.query.order_by(User.tasks_solved.desc()).limit(10).all()
    popular_categories = db.session.query(
        Category.name, func.count(Task.id).label('count')
    ).join(Task).group_by(Category.id).order_by(func.count(Task.id).desc()).limit(5).all()
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    daily_stats = Statistics.query.filter(
        Statistics.date >= start_date, Statistics.date <= end_date
    ).order_by(Statistics.date.asc()).all()
    return render_template('statistics.html', title='Статистика', total_users=total_users, total_tasks=total_tasks,
                           total_solves=total_solves, total_comments=total_comments, top_users=top_users,
                           top_creators=top_creators, top_solvers=top_solvers, popular_categories=popular_categories,
                           daily_stats=daily_stats)


@bp.route('/about')
def about():
    return render_template('about.html', title='О проекте')