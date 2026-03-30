from flask import Flask, render_template, redirect
from flask_login import login_user, LoginManager, logout_user, login_required
from flask_restful import Api

from data import db_session, jobs_api, users_resource
from data.loginform import LoginForm
from data.news import News
from data.users import User
from data.jobs import Jobs
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(Jobs, user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Jobs).filter(Jobs.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main(news_api=None):
    print('fdsfs')
    db_session.global_init("db/blogs.db")
    app.register_blueprint(jobs_api.blueprint)
    api.add_resource(users_resource.NewsListResource, '/api/v2/users')
    api.add_resource(users_resource.NewsResource, '/api/v2/users/<int:users_id>')

    '''user = User()
    user.name = "Пользователь 1"
    user.about = "биография пользователя 1"
    user.email = "email2@email.ru"
    user.set_password("123452")
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()

    job = Jobs()
    job.team_leader = "1"
    job.job = "Программист"
    job.work_size = 5
    job.collaborators = "Что-то"
    db_sess = db_session.create_session()
    db_sess.add(job)
    db_sess.commit()'''

    app.run()


if __name__ == '__main__':
    main()