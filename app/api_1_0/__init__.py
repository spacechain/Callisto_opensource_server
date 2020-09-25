# -*- coding: utf-8 -*-

from flask import Blueprint

api_1_0 = Blueprint('api_1_0', __name__)

from app.api_1_0 import sign, wallet, terms, anthenticator, fee, send_verify_code
