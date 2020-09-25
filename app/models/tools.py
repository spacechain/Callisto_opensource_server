# -*- coding: utf-8 -*-
import uuid
import base64
import os
import re


def get_secret_key():
    """
    随机生成otp——secret_key
    :return:
    """
    return base64.b32encode(os.urandom(10)).decode('utf-8')


def re_email(email):
    """
    正则校验email
    :param email:
    :return:
    """

    if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
        return True

    return False


def get_uuid():
    """
    model的ID为UUID，非数字
    :return:
    """
    return uuid.uuid4().hex


