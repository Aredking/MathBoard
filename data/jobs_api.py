import flask
from flask import jsonify, make_response

from . import db_session
from .jobs import Jobs

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs')
def get_news():
    db_sess = db_session.create_session()
    news = db_sess.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict()
                 for item in news]
        }
    )


@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_one_job(job_id):
    db_sess = db_session.create_session()
    jobs = db_sess.get(Jobs, job_id)
    if not jobs:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'jobs':
                jobs.to_dict()
        }
    )
