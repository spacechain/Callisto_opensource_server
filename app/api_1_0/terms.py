# -*- coding: utf-8 -*-
from app.api_1_0 import api_1_0
from flask_restful.reqparse import RequestParser
from flask import jsonify, request
from app.tools import get_logger
import constants

parser = RequestParser()

logger = get_logger(__name__)


@api_1_0.before_request
def create_logging():
    if request.method == 'GET':
        logger.info(request.args)
    elif request.method == 'POST':
        logger.info(request.form)


@api_1_0.route('/terms', methods=['get'])
def get_terms():
    """
    获取条款信息
    :return:
    """
    return jsonify({
        'data': constants.TERMS
    })
