from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.constants import SUCCESS_REGISTER, SUCCESS_LOGIN, SUCCESS_LOGOUT
from datetime import datetime


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        user.last_seen = datetime.utcnow()
        db.session.commit()
        flash(SUCCESS_LOGIN.format(user.name), 'success')
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('tasks.index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(SUCCESS_LOGOUT, 'info')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tasks.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            name=form.name.data,
            email=form.email.data if form.email.data else None
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(SUCCESS_REGISTER, 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Регистрация', form=form)