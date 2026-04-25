from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.tasks import bp
from app.models import Task, Category, Like, Favorite, Comment
from app.forms import TaskForm, SearchForm, AnswerCheckForm, CommentForm
from app.utils import save_uploaded_file, delete_uploaded_file
from app.decorators import task_owner_required, log_action, rate_limit
from app.constants import (
    SUCCESS_TASK_CREATED, SUCCESS_TASK_UPDATED, SUCCESS_TASK_DELETED,
    SUCCESS_ANSWER_CORRECT, SUCCESS_ANSWER_WRONG,
    ACTION_TYPE_CREATE_TASK, ACTION_TYPE_EDIT_TASK, ACTION_TYPE_DELETE_TASK,
    ACTION_TYPE_SOLVE_TASK, ACTION_TYPE_LIKE_TASK, ACTION_TYPE_FAVORITE_TASK,
    TASK_STATUS_ACTIVE
)
from datetime import datetime


@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    form = SearchForm(request.args)
    query = Task.query.filter_by(status=TASK_STATUS_ACTIVE)
    if form.q.data:
        query = query.filter(Task.title.contains(form.q.data))
    if form.category.data:
        query = query.filter_by(category_id=form.category.data)
    if form.difficulty.data:
        query = query.filter_by(difficulty=form.difficulty.data)
    sort = form.sort_by.data or 'created_at_desc'
    if sort == 'created_at_desc':
        query = query.order_by(Task.created_at.desc())
    elif sort == 'created_at_asc':
        query = query.order_by(Task.created_at.asc())
    elif sort == 'likes_desc':
        query = query.order_by(Task.likes_count.desc())
    elif sort == 'solves_desc':
        query = query.order_by(Task.solves_count.desc())
    elif sort == 'views_desc':
        query = query.order_by(Task.views.desc())
    pagination = query.paginate(page=page, per_page=current_app.config['TASKS_PER_PAGE'], error_out=False)
    tasks = pagination.items
    return render_template('index.html', title='Главная', tasks=tasks, pagination=pagination, form=form)


@bp.route('/task/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    task.increment_views()
    comment_form = CommentForm(task_id=task_id)
    answer_form = AnswerCheckForm(task_id=task_id)
    comments = Comment.query.filter_by(task_id=task_id, status='active').order_by(Comment.created_at.desc()).all()
    return render_template('task_detail.html', title=task.title[:50], task=task, comments=comments,
                           comment_form=comment_form, answer_form=answer_form)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@log_action(ACTION_TYPE_CREATE_TASK)
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            answer=form.answer.data,
            solution=form.solution.data,
            hint=form.hint.data,
            difficulty=form.difficulty.data,
            category_id=form.category.data,
            author=current_user
        )
        if form.file.data:
            task.filename = save_uploaded_file(form.file.data, subfolder='tasks')
        db.session.add(task)
        current_user.tasks_created += 1
        current_user.update_reputation()
        db.session.commit()
        flash(SUCCESS_TASK_CREATED, 'success')
        return redirect(url_for('tasks.task_detail', task_id=task.id))
    return render_template('task_form.html', title='Новая задача', form=form, legend='Создать задачу')


@bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
@task_owner_required
@log_action(ACTION_TYPE_EDIT_TASK)
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.answer = form.answer.data
        task.solution = form.solution.data
        task.hint = form.hint.data
        task.difficulty = form.difficulty.data
        task.category_id = form.category.data
        task.updated_at = datetime.utcnow()
        if form.file.data:
            if task.filename:
                delete_uploaded_file(task.filename, subfolder='tasks')
            task.filename = save_uploaded_file(form.file.data, subfolder='tasks')
        db.session.commit()
        flash(SUCCESS_TASK_UPDATED, 'success')
        return redirect(url_for('tasks.task_detail', task_id=task.id))
    return render_template('task_form.html', title='Редактирование', form=form, legend='Редактировать задачу')


@bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
@task_owner_required
@log_action(ACTION_TYPE_DELETE_TASK)
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.filename:
        delete_uploaded_file(task.filename, subfolder='tasks')
    db.session.delete(task)
    current_user.tasks_created = max(0, current_user.tasks_created - 1)
    current_user.update_reputation()
    db.session.commit()
    flash(SUCCESS_TASK_DELETED, 'success')
    return redirect(url_for('tasks.index'))


@bp.route('/check_answer/<int:task_id>', methods=['POST'])
@login_required
@rate_limit(max_requests=20, window_seconds=60)
def check_answer(task_id):
    task = Task.query.get_or_404(task_id)
    form = AnswerCheckForm()
    if form.validate_on_submit():
        is_correct = task.check_answer(form.answer.data)
        if is_correct:
            task.solves_count += 1
            current_user.tasks_solved += 1
            current_user.update_reputation()
            db.session.commit()
            return jsonify({'status': 'correct', 'message': SUCCESS_ANSWER_CORRECT})
        else:
            return jsonify({'status': 'wrong', 'message': SUCCESS_ANSWER_WRONG})
    return jsonify({'status': 'error', 'message': 'Ошибка валидации'}), 400


@bp.route('/like/<int:task_id>', methods=['POST'])
@login_required
@log_action(ACTION_TYPE_LIKE_TASK)
def like_task(task_id):
    task = Task.query.get_or_404(task_id)
    existing = Like.query.filter_by(user_id=current_user.id, task_id=task_id).first()
    if existing:
        db.session.delete(existing)
        task.likes_count = max(0, task.likes_count - 1)
        liked = False
    else:
        like = Like(user_id=current_user.id, task_id=task_id)
        db.session.add(like)
        task.likes_count += 1
        liked = True
        if task.author != current_user:
            task.author.total_likes_received += 1
            task.author.update_reputation()
    db.session.commit()
    return jsonify({'liked': liked, 'count': task.likes_count})


@bp.route('/favorite/<int:task_id>', methods=['POST'])
@login_required
@log_action(ACTION_TYPE_FAVORITE_TASK)
def favorite_task(task_id):
    task = Task.query.get_or_404(task_id)
    existing = Favorite.query.filter_by(user_id=current_user.id, task_id=task_id).first()
    if existing:
        db.session.delete(existing)
        favorited = False
    else:
        fav = Favorite(user_id=current_user.id, task_id=task_id)
        db.session.add(fav)
        favorited = True
    db.session.commit()
    return jsonify({'favorited': favorited})