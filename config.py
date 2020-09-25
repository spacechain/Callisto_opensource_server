# -*- coding: utf-8 -*-
import account_config

import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    配置
    """

    # 作用于将交易信息发送给地面站，继而发送给卫星签名，以及获取签完名的交易信息
    FTP_IP = '18.189.57.10'  # FTP服务器IP
    FTP_USER = account_config.EOYDVGJ.replace(' ', '')
    FTP_PWD = account_config.WCTSIGB.replace(' ', '')  # FTP密码
    FTP_UPLOAD_PATH = 'download/'  # FTP下传文件路径
    FTP_DOWNLOAD_PATH = 'upload/'  # FTP上传文件路径

    # 该邮箱用于给用户发送"取消交易"等系统邮件
    MAIL_SERVER = account_config.MAIL_SERVER.replace(' ', '')  # SMTP服务器地址
    MAIL_PORT = account_config.MAIL_PORT  # SMTP服务器端口
    MAIL_USERNAME = account_config.MAIL_USERNAME.replace(' ', '')  # 邮箱地址
    MAIL_PASSWORD = account_config.MAIL_PASSWORD.replace(' ', '')  # 邮箱SMTP密码
    MAIL_USE_SSL = True

    # 测试环境收费钱包XPUB
    FEE_XPUB_BY_TESTNET = account_config.FEE_XPUB_BY_TESTNET.replace(' ', '')
    # 主网环境收费钱包XPUB
    FEE_XPUB = account_config.FEE_XPUB.replace(' ', '')

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_TEARDOWN = True
    # 连接bandwagon数据库
    SQLALCHEMY_DATABASE_URI = account_config.SQLALCHEMY_DATABASE_URI.replace(' ', '')

    # LOG
    LOG_LEVEL = logging.DEBUG
    LOG_FILEMODE = 'a'
    LOG_FORMAT = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    LOG_FILE_PATH = '/home/tc/server_log/tc-server-request.log'

    PACK_FILE_PATH = '/home/tc/pack_files/'
    DOWNLOAD_FILE_PATH = '/home/tc/tc_download_files/'
    SECRET_PNG_PATH = basedir + '/app/static/secret_key.png'

    @staticmethod
    def init_app(app):
        pass


config = {
    'default': Config
}
