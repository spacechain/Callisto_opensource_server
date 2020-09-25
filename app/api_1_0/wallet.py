# -*- coding: utf-8 -*-
from app.api_1_0 import api_1_0
from app import db
from app.models import Wallet, SatXpub
from flask_restful.reqparse import RequestParser
from flask import jsonify, request
from app.tools import get_logger, re_email
import json
from bip32 import constants
import constants as tc_constants
import random

parser = RequestParser()

logger = get_logger(__name__)


@api_1_0.before_request
def create_logging():
    if request.method == 'GET':
        logger.info(request.args)
    elif request.method == 'POST':
        logger.info(request.json)


@api_1_0.route('/create_wallet', methods=['post'])
def create_wallet():
    """
    创建钱包
    :return:
    """
    req = request.data.decode()
    req = json.loads(req)

    email = req.get('email_address')
    first_xpub = req.get('first_xpub')
    secondary_xpub = req.get('secondary_xpub')
    is_test = req.get('is_test', None)
    type_of_service = req.get('type_of_service')

    if not email \
            or not first_xpub \
            or not secondary_xpub \
            or is_test is None \
            or is_test not in [tc_constants.BITCOIN_MAIN, tc_constants.BITCOIN_TEST] \
            or type_of_service not in [tc_constants.WALLET_TYPE_ENTERPRISE, tc_constants.WALLET_TYPE_PERSONAL,
                                       tc_constants.WALLET_TYPE_SPACECHAIN]:
        logger.info('==========invalid args==========%s' % str(req))
        return jsonify({'message': 'invalid args', "status": 400, }), 400

    if not re_email(email):
        logger.info('==========email error==========%s' % str(email))
        return jsonify({'message': 'invalid email', "status": 400, }), 400

    # 查询钱包是否存在
    wallet_info = Wallet.query.filter_by(first_xpub=first_xpub, secondary_xpub=secondary_xpub).first()
    if wallet_info:
        wallet_info.email = email
        wallet_info.otp_index = 1
        db.session.add(wallet_info)
        db.session.commit()

        # 随意交换下字符串顺序 客户端再拼装
        otp_secret_key = wallet_info.otp_secret_key[5:] + wallet_info.otp_secret_key[:5]
        sat_xpub = wallet_info.sat_xpub_info.xpub
        sat_xpub = sat_xpub[5:] + sat_xpub[:5]
        return jsonify({
            'otp_secret': otp_secret_key,
            'sat_xpub': sat_xpub
        })

    # 随机分配
    sats = SatXpub.query.filter_by(is_testnet=tc_constants.BITCOIN_MAIN)
    rand = random.randrange(0, sats.count())
    sat_info = sats[rand]
    constants.set_mainnet()

    sat_xpub = sat_info.xpub

    long_id, short_id = Wallet.get_user_id(first_xpub, secondary_xpub)

    wallet = Wallet(email=email, first_xpub=first_xpub, secondary_xpub=secondary_xpub, sat_xpub_id=sat_info.id,
                    short_id=short_id, is_testnet=is_test, type_of_service=type_of_service)

    db.session.add(wallet)
    db.session.commit()
    wallet.billing_address = Wallet.make_billing_address(wallet.id)
    db.session.commit()

    # 随意交换下字符串顺序 客户端再拼装
    otp_secret_key = wallet.otp_secret_key[5:] + wallet.otp_secret_key[:5]
    sat_xpub = sat_xpub[5:] + sat_xpub[:5]
    if "\x00" in sat_xpub:
        sat_xpub = sat_xpub.replace("\x00", '')

    return jsonify({
        'otp_secret': otp_secret_key,
        'sat_xpub': sat_xpub
    })
