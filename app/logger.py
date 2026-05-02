"""
Модуль логирования.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from flask import request, has_request_context


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.ip = request.remote_addr
            record.user_id = getattr(request, 'user_id', 'anonymous')
        else:
            record.url = record.method = record.ip = None
            record.user_id = 'system'
        return super().format(record)


class UserActionLogger:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def log(self, action_type, details=None, user=None):
        if not user and has_request_context():
            from flask_login import current_user
            if current_user.is_authenticated:
                user = current_user
        if user:
            from app.models import UserActionLog
            from app import db
            log_entry = UserActionLog(
                user_id=user.id,
                action_type=action_type,
                details=str(details) if details else None,
                ip_address=request.remote_addr if has_request_context() else None,
                user_agent=request.user_agent.string if has_request_context() else None
            )
            db.session.add(log_entry)
            db.session.commit()


def setup_app_logger(app):
    log_dir = os.path.join(os.path.dirname(app.root_path), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    formatter = RequestFormatter('[%(asctime)s] %(levelname)s - %(user_id)s@%(ip)s: %(message)s')
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'mathboard.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Приложение запущено')


action_logger = UserActionLogger()