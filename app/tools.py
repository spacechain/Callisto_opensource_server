# -*- coding: utf-8 -*-
from flask import current_app, render_template
from flask_mail import Message
from app import mail
import random
from threading import Thread
import logging
from config import config
import re
import ftplib
import base64, struct, hmac, hashlib


def get_logger(main_name):
    c = config['default']

    logging.basicConfig(level=c.LOG_LEVEL, filename=c.LOG_FILE_PATH, filemode=c.LOG_FILEMODE, format=c.LOG_FORMAT)

    logger = logging.getLogger(main_name)

    return logger


logger = get_logger(__name__)


def re_email(email):
    """
    正则校验email
    :param email:
    :return:
    """

    if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
        return True

    return False


def get_code(max):
    code = ""
    for i in range(max):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        code += ch
    return code


def send_async_email(app, msg):
    try:
        logger.info('===================send_async_email start===================')

        with app.app_context():
            mail.send(msg)
        logger.info('===================send_async_email end===================')

    except  Exception as e:
        logger.info('===================send_async_email err===========%s========' % e)


def send_email(to, code, **kwargs):
    """
    web注册页面发送验证码
    :param to:
    :param code:
    :param kwargs:
    :return:
    """
    app = current_app._get_current_object()
    message = Message("Verification code", sender=current_app.config["MAIL_USERNAME"], recipients=[to])
    message.html = render_template('email.html', code=code)
    thr = Thread(target=send_async_email, args=[app, message])
    thr.start()
    return thr


def ftp_upload(local_file_name):
    """
    FTP上传
    :param local_file_name:
    :return:
    """
    f = ftplib.FTP(current_app.config["FTP_IP"])  # 实例化FTP对象

    f.login(current_app.config["FTP_USER"], current_app.config["FTP_PWD"])  # 登录
    f.set_pasv(True)

    f.cwd(current_app.config["FTP_UPLOAD_PATH"])

    pwd_path = f.pwd()
    logger.info('===================FTP PATH===================%s' % str(pwd_path))
    logger.info('===================local_file_name===================%s' % str(local_file_name))

    file_remote = local_file_name
    file_local = current_app.config["PACK_FILE_PATH"] + local_file_name
    fp = open(file_local, 'rb')
    f.storbinary('STOR ' + file_remote, fp)
    fp.close()
    f.quit()


def get_google_code(secret_key, num):
    """
    基于计数器的算法 计算出五次以内的所有OTP
    :param secret_key:
    :return:
    """
    decode_secret = base64.b32decode(secret_key, True)
    # 解码 Base32 编码过的 bytes-like object 或 ASCII 字符串 s 并返回解码过的 bytes。

    result = {}

    for interval_number in range(num, num + 5):
        message = struct.pack(">Q", interval_number)
        digest = hmac.new(decode_secret, message, hashlib.sha1).digest()
        index = ord(chr(digest[19])) % 16
        google_code = (struct.unpack(">I", digest[index:index + 4])[0] & 0x7fffffff) % 1000000

        result[interval_number] = "%06d" % google_code

    return result
