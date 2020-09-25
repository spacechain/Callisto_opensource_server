# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, request
from app.auth import auth
from flask_login import login_required, login_user, logout_user
from app.auth.forms import LoginForm, RegistrationForm
from flask import flash
from app.models import User, AuthVerifyCode
from app import db
from app.tools import get_logger
import constants

logger = get_logger(__name__)


@auth.before_request
def create_logging():
    if request.method == 'GET':
        logger.info(request.args)
    elif request.method == 'POST':
        logger.info(request.form)


@auth.route('/login', methods=['POST', 'GET'])
def login():
    """
    登录
    :return:
    """
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        pwd = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Incorrect username.')
            return render_template('auth/login.html', form=form)

        if not user.verify_password(pwd):
            flash('Incorrect password.')
            return render_template('auth/login.html', form=form)

        login_user(user, form.remember_me.data)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['POST', 'GET'])
def register():
    """
    注册
    :return:
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        password = form.password.data
        email = form.email.data
        verify_code = form.verify_code.data

        if not AuthVerifyCode.re_email(email):
            flash('Email format error.')
            return render_template('auth/register.html', form=form)

        obj_user = User.query.filter_by(email=email, state=constants.USER_ENABLE).first()
        if obj_user:
            flash('The mailbox has been registered.')
            return render_template('auth/register.html', form=form)

        obj_code = AuthVerifyCode.query.filter_by(email=email, verify_code=verify_code,
                                                  state=constants.VERIFY_CODE_ENABLE).first()
        if not obj_code:
            flash('Code is invalid.')
            return render_template('auth/register.html', form=form)

        obj_code.state = constants.VERIFY_CODE_DISABLE
        db.session.add(obj_code)
        db.session.commit()

        # 已过期 超过60秒
        if not AuthVerifyCode.check_code_timedelta(obj_code.created_at):
            flash('Code is invalid.')
            return render_template('auth/register.html', form=form)

        user = User(email=email, password=password, )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('main.index'))

    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/secret')
@login_required
def secret():
    return render_template('base.html')
