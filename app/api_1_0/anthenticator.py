# -*- coding: utf-8 -*-
from app.api_1_0 import api_1_0
from flask_restful.reqparse import RequestParser
from flask import jsonify, request
from app.tools import get_logger, get_google_code
from app.models import Wallet
from app import db

parser = RequestParser()

logger = get_logger(__name__)


@api_1_0.before_request
def create_logging():
    if request.method == 'GET':
        logger.info(request.args)
    elif request.method == 'POST':
        logger.info(request.form)


@api_1_0.route('/check_code', methods=['get'])
def check_code():
    """
    谷歌身份验证 OTP校验
    :return:
    """
    parser.add_argument('short_id', type=str, required=True, nullable=False, location=['args', 'json'])
    parser.add_argument('otp', type=str, required=True, nullable=False, location=['args', 'json'])
    parser.add_argument('is_test', type=str, required=True, nullable=False, location=['args', 'json'])
    req = parser.parse_args(strict=True)

    code = str(req.get('otp'))
    short_id = req.get('short_id')
    wallet_info = Wallet.query.filter_by(short_id=short_id).first()

    secret_key = wallet_info.otp_secret_key

    otp_index = wallet_info.otp_index

    code_result = get_google_code(secret_key, otp_index)

    if code in code_result.values():
        otp_index = list(code_result.keys())[list(code_result.values()).index(code)]
        wallet_info.otp_index = int(otp_index)
        db.session.add(wallet_info)
        db.session.commit()
        return jsonify({
            'succeed': True,
            'google_code': code,
        })
    else:
        logger.info('==========otp error==========otp:%s,otp_list:%s' % (code, str(code_result.values())))
        return jsonify({
            "status": 400,
            "message": "invalid otp"
        }), 400
