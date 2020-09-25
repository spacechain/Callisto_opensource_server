# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Length(1, 64),
                                             Regexp('^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', 0,
                                                    'Wrong email address')])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('submit')


class RegistrationForm(FlaskForm):
    email = StringField('email', validators=[
        Regexp('^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', 0, 'Wrong email address'), DataRequired()])

    verify_code = StringField('verification code', validators=[DataRequired(), Length(6, 6, 'Verification code')])

    password = PasswordField('password', validators=[DataRequired(), Length(6, 16),
                                                     EqualTo('password_again', message='The password is different')])

    password_again = PasswordField('password again', validators=[DataRequired()])
    submit = SubmitField('submit')
