from flask import Flask, jsonify
from flask_restful import abort, Api, Resource
from werkzeug.security import generate_password_hash

from data import db_session
from data.parsers import parser
from data.users import User


def set_password(self, password):
    self.hashed_password = generate_password_hash(password)


def abort_if_users_not_found(users_id):
    session = db_session.create_session()
    users = session.query(User).get(users_id)
    if not users:
        abort(404, message=f"User {users_id} not found")


class NewsResource(Resource):
    def get(self, users_id):
        abort_if_users_not_found(users_id)
        session = db_session.create_session()
        users = session.get(User, users_id)
        return jsonify({'user': users.to_dict()})

    def delete(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.get(User, user_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})


class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'user': [item.to_dict() for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        users = User(
            id=args['id'],
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            hashed_password=args['hashed_password'],
            modified_date=args['modified_date']
        )
        session.add(users)
        session.commit()
        return jsonify({'id': users.id})
