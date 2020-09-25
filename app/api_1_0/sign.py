# -*- coding: utf-8 -*-
from app.api_1_0 import api_1_0
from app import db
from app.models import Wallet, TransactionRecord
from flask_restful.reqparse import RequestParser
from flask import jsonify, request
from app.tools import get_logger, get_google_code
import json
import constants

parser = RequestParser()

logger = get_logger(__name__)


@api_1_0.before_request
def create_logging():
    if request.method == 'GET':
        logger.info(request.args)
    elif request.method == 'POST':
        logger.info(request.json)


@api_1_0.route('/sign', methods=['post'])
def sign():
    """
    交易签名
    :return:签名未完成 待卫星签名
    """

    req = request.data.decode()
    req = json.loads(req)

    short_id = req.get('short_id')
    raw_tx = req.get('raw_tx')
    otp = str(req.get('otp'))
    is_test = req.get('is_test', None)

    if not raw_tx or not otp or not short_id or is_test is None or is_test not in [constants.BITCOIN_MAIN,
                                                                                   constants.BITCOIN_MAIN]:
        logger.info('==========invalid args==========%s' % str(req))
        return jsonify({
            "status": 400,
            'message': 'Invalid args'
        }), 400

    wallet_info = Wallet.query.filter_by(short_id=short_id, state=constants.WALLET_ENABLE).first()
    if not wallet_info:
        logger.info('==========not found wallet==========short_id:%s' % short_id)
        return jsonify({
            "status": 400,
            "message": "No wallet file found"
        }), 400

    # 交易次数是否足够
    tx_remaining = wallet_info.tx_remaining

    if not (tx_remaining >= 0):
        logger.info('==========Lack of remaining==========tx_remaining:%s' % tx_remaining)
        return jsonify({
            "status": 400,
            "message": "Lack of remaining"
        }), 400
    wallet_info.tx_remaining = tx_remaining - 1

    # OTP 验证
    secret_key = wallet_info.otp_secret_key

    otp_index = wallet_info.otp_index

    code_result = get_google_code(secret_key, otp_index)

    if otp not in code_result.values():
        logger.info('==========otp error==========otp:%s,otp_list:%s' % (str(otp), str(code_result.values())))
        return jsonify({
            "status": 400,
            "message": "Invalid otp"
        }), 400

    # 更改otp次数
    otp_index = list(code_result.keys())[list(code_result.values()).index(otp)]
    wallet_info.otp_index = int(otp_index)
    db.session.add(wallet_info)
    db.session.commit()

    if wallet_info.type_of_service == constants.WALLET_TYPE_ENTERPRISE:
        delayed_type = constants.WALLET_TYPE_DELAYED
    else:
        delayed_type = constants.WALLET_TYPE_NOT_DELAYED

    # 保存至交易记录表
    transaction = TransactionRecord(wallet_id=wallet_info.id, raw_tx_hex=raw_tx,
                                    state=constants.TRANSACTION_STATE_WAITING, delayed_type=delayed_type)

    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        'transaction': 'Waiting for the signature'
    }), 200
