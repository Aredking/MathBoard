from flask import redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.comments import bp
from app.models import Comment, Task
from app.forms import CommentForm
from app.decorators import comment_owner_required, log_action
from app.constants import ACTION_TYPE_ADD_COMMENT, SUCCESS_COMMENT_ADDED, SUCCESS_COMMENT_DELETED


@bp.route('/add', methods=['POST'])
@login_required
@log_action(ACTION_TYPE_ADD_COMMENT)
def add_comment():
    form = CommentForm()
    if form.validate_on_submit():
        task = Task.query.get_or_404(form.task_id.data)
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            task_id=form.task_id.data,
            parent_id=form.parent_id.data if form.parent_id.data else None
        )
        db.session.add(comment)
        task.comments_count += 1
        db.session.commit()
        flash(SUCCESS_COMMENT_ADDED, 'success')
        return redirect(url_for('tasks.task_detail', task_id=task.id))
    flash('Ошибка при добавлении комментария', 'danger')
    return redirect(request.referrer or url_for('tasks.index'))


@bp.route('/delete/<int:comment_id>', methods=['POST'])
@login_required
@comment_owner_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    task_id = comment.task_id
    db.session.delete(comment)
    Task.query.get(task_id).comments_count = max(0, Task.query.get(task_id).comments_count - 1)
    db.session.commit()
    flash(SUCCESS_COMMENT_DELETED, 'success')
    return redirect(url_for('tasks.task_detail', task_id=task_id))


@bp.route('/reply/<int:comment_id>', methods=['POST'])
@login_required
def reply_comment(comment_id):
    parent = Comment.query.get_or_404(comment_id)
    content = request.form.get('content')
    if not content or len(content) < 2:
        return jsonify({'error': 'Текст комментария слишком короткий'}), 400
    reply = Comment(
        content=content,
        user_id=current_user.id,
        task_id=parent.task_id,
        parent_id=parent.id
    )
    db.session.add(reply)
    Task.query.get(parent.task_id).comments_count += 1
    db.session.commit()
    return jsonify({'success': True, 'comment': {
        'id': reply.id,
        'content': reply.content,
        'author': reply.author.name,
        'created_at': reply.created_at.strftime('%d.%m.%Y %H:%M')
    }})