from flask import render_template, jsonify
from app import db


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(429)
    def too_many_requests(e):
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        app.logger.error(f'Server Error: {e}')
        return render_template('errors/500.html'), 500