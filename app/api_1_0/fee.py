# -*- coding: utf-8 -*-
from app.api_1_0 import api_1_0
from flask_restful.reqparse import RequestParser
from flask import jsonify, request
from app.tools import get_logger
from app.models import Wallet

parser = RequestParser()

logger = get_logger(__name__)


@api_1_0.before_request
def create_logging():
    if request.method == 'GET':
        logger.info(request.args)
    elif request.method == 'POST':
        logger.info(request.form)


@api_1_0.route('/get_billing', methods=['get'])
def get_billing():
    """
    获取费用信息
    :return:
    """
    parser.add_argument('short_id', type=str, required=True, nullable=False, location=['args', 'json'])
    req = parser.parse_args(strict=True)

    short_id = req.get('short_id')

    wallet_info = Wallet.query.filter_by(short_id=short_id).first()

    # result = {'billing_plan': 'electrum-per-tx-otp',
    #           'billing_address': 'mhArEhjwVxfLoRNU1S3UVRRQSaTLTsPGF1', 'network': 'testnet',
    #           'tx_remaining': 0, 'billing_index': 0,
    #           'billing_address_segwit': 'tb1qzg3wqfy45j44vvaj0k0xkr7rc0l64xj9k2avmg',
    #           'price_per_tx': [[1, 50000], [20, 100000], [100, 250000]],
    #           'id': '64acb16fa4e8ad05520e73e1d599fda5dba83a8024796bb69bf9ea90a0b55293'}
    # todo trustcoin参数的意义
    result = {
        'billing_plan': 'electrum-per-tx-otp',
        'billing_address': wallet_info.billing_address,
        'tx_remaining': wallet_info.tx_remaining,
        'billing_index': 1,
        'billing_address_segwit': wallet_info.billing_address,
        'price_per_tx': [[1, 50000], [20, 100000], [100, 250000]],
        'id': wallet_info.id
    }

    return jsonify(result)
