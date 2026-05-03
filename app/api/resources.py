from flask import request, jsonify
from flask_restful import Resource, abort, reqparse
from flask_login import current_user
from app import db
from app.models import User, Task, Comment, Category
from sqlalchemy import func


def abort_if_task_not_found(task_id):
    if not Task.query.get(task_id):
        abort(404, message=f"Task {task_id} not found")

def abort_if_user_not_found(user_id):
    if not User.query.get(user_id):
        abort(404, message=f"User {user_id} not found")

def abort_if_comment_not_found(comment_id):
    if not Comment.query.get(comment_id):
        abort(404, message=f"Comment {comment_id} not found")


task_parser = reqparse.RequestParser()
task_parser.add_argument('title', required=True)
task_parser.add_argument('answer', required=True)
task_parser.add_argument('solution')
task_parser.add_argument('hint')
task_parser.add_argument('difficulty', default='medium')
task_parser.add_argument('category_id', type=int)
task_parser.add_argument('status', default='active')

comment_parser = reqparse.RequestParser()
comment_parser.add_argument('content', required=True)
comment_parser.add_argument('task_id', type=int, required=True)
comment_parser.add_argument('parent_id', type=int)


class TaskListResource(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category = request.args.get('category', type=int)
        difficulty = request.args.get('difficulty')
        search = request.args.get('q')
        query = Task.query.filter_by(status='active')
        if category:
            query = query.filter_by(category_id=category)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        if search:
            query = query.filter(Task.title.contains(search))
        pagination = query.order_by(Task.created_at.desc()).paginate(page=page, per_page=per_page)
        return jsonify({
            'tasks': [t.to_dict() for t in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    def post(self):
        if not current_user.is_authenticated:
            abort(401)
        args = task_parser.parse_args()
        task = Task(
            title=args['title'],
            answer=args['answer'],
            solution=args.get('solution'),
            hint=args.get('hint'),
            difficulty=args.get('difficulty', 'medium'),
            category_id=args.get('category_id'),
            user_id=current_user.id,
            status='pending'
        )
        db.session.add(task)
        current_user.tasks_created += 1
        db.session.commit()
        return task.to_dict(), 201


class TaskResource(Resource):
    def get(self, task_id):
        abort_if_task_not_found(task_id)
        return Task.query.get(task_id).to_dict()

    def put(self, task_id):
        abort_if_task_not_found(task_id)
        if not current_user.is_authenticated:
            abort(401)
        task = Task.query.get(task_id)
        if current_user.id != task.user_id and current_user.role != 'admin':
            abort(403)
        args = task_parser.parse_args()
        task.title = args['title']
        task.answer = args['answer']
        task.solution = args.get('solution')
        task.hint = args.get('hint')
        task.difficulty = args.get('difficulty', task.difficulty)
        if args.get('category_id'):
            task.category_id = args['category_id']
        db.session.commit()
        return task.to_dict()

    def delete(self, task_id):
        abort_if_task_not_found(task_id)
        if not current_user.is_authenticated:
            abort(401)
        task = Task.query.get(task_id)
        if current_user.id != task.user_id and current_user.role != 'admin':
            abort(403)
        db.session.delete(task)
        db.session.commit()
        return {'message': 'Task deleted'}, 200


class UserListResource(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        pagination = User.query.order_by(User.reputation.desc()).paginate(page=page, per_page=per_page)
        return jsonify({
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages
        })


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        return User.query.get(user_id).to_dict()


class CommentListResource(Resource):
    def get(self):
        task_id = request.args.get('task_id', type=int)
        if not task_id:
            abort(400, message="task_id required")
        comments = Comment.query.filter_by(task_id=task_id, status='active').order_by(Comment.created_at.asc()).all()
        return jsonify([c.to_dict() for c in comments])

    def post(self):
        if not current_user.is_authenticated:
            abort(401)
        args = comment_parser.parse_args()
        task = Task.query.get(args['task_id'])
        if not task:
            abort(404, message="Task not found")
        comment = Comment(
            content=args['content'],
            user_id=current_user.id,
            task_id=args['task_id'],
            parent_id=args.get('parent_id')
        )
        db.session.add(comment)
        task.comments_count += 1
        db.session.commit()
        return comment.to_dict(), 201


class CommentResource(Resource):
    def delete(self, comment_id):
        abort_if_comment_not_found(comment_id)
        if not current_user.is_authenticated:
            abort(401)
        comment = Comment.query.get(comment_id)
        if current_user.id != comment.user_id and current_user.role != 'admin':
            abort(403)
        db.session.delete(comment)
        db.session.commit()
        return {'message': 'Comment deleted'}, 200


class CategoryListResource(Resource):
    def get(self):
        categories = Category.query.order_by(Category.order).all()
        return jsonify([c.to_dict() for c in categories])


class StatisticsResource(Resource):
    def get(self):
        total_users = User.query.count()
        total_tasks = Task.query.filter_by(status='active').count()
        total_solves = db.session.query(func.sum(Task.solves_count)).scalar() or 0
        top_categories = db.session.query(
            Category.name, func.count(Task.id).label('count')
        ).join(Task).group_by(Category.id).order_by(func.count(Task.id).desc()).limit(5).all()
        return jsonify({
            'total_users': total_users,
            'total_tasks': total_tasks,
            'total_solves': total_solves,
            'top_categories': [{'name': name, 'count': count} for name, count in top_categories]
        })