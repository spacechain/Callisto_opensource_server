# -*- coding: utf-8 -*-
from app.api_1_0 import api_1_0
from flask import jsonify, request
from app.models import User, Wallet, AuthVerifyCode
from flask_restful.reqparse import RequestParser
from app.tools import get_logger

parser = RequestParser()

logger = get_logger(__name__)


@api_1_0.before_request
def create_logging():
    if request.method == 'GET':
        logger.info(request.args)
    elif request.method == 'POST':
        logger.info(request.form)


@api_1_0.route('/send_code_by_email/', methods=['post'])
def send_code_by_email():
    """
    WEB注册界面 发送验证码
    :return:
    """
    parser.add_argument('email', type=str, required=True, nullable=False, location=['form'])

    req = parser.parse_args(strict=True)
    email = req.get('email')
    rsp = {
        'succeed': True,
        'error_message': ''
    }

    if not AuthVerifyCode.re_email(email):
        rsp = {
            'succeed': False,
            'error_message': 'Email format error.'
        }
        return jsonify(rsp), 400

    AuthVerifyCode.send_code_thr(email)

    return jsonify(rsp)
