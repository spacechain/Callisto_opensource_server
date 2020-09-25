# -*- coding: utf-8 -*-

from app import db
from app.models.tools import get_uuid
from datetime import datetime
import re
import random
from app.tools import send_email
import constants


class AuthVerifyCode(db.Model):
    """
    验证码发送记录表
    """

    __tablename__ = 'auth_verify_code'

    id = db.Column(db.String(32), default=get_uuid, primary_key=True, unique=True, index=True, nullable=False)

    email = db.Column(db.String(64), index=True, nullable=False)

    verify_code = db.Column(db.Integer, nullable=False)

    state = db.Column(db.Integer, nullable=False, default=constants.VERIFY_CODE_ENABLE)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    @staticmethod
    def re_email(email):
        """
        正则校验email
        :param email:
        :return:
        """
        if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
            return True

        return False

    @staticmethod
    def check_code_timedelta(created_at):
        """
        判断验证码是否过期
        :param created_at:
        :return:
        """
        created_timedelta = datetime.utcnow() - created_at

        # 已过期 超过60秒
        if created_timedelta.total_seconds() > constants.VERIFY_CODE_PERIOD_OF_VALIDITY:
            return False

        return True

    @staticmethod
    def get_code(max_len):
        code = ""
        for i in range(max_len):
            ch = chr(random.randrange(ord('0'), ord('9') + 1))
            code += ch
        return code

    @staticmethod
    def send_code_thr(email):
        """
        WEB注册界面 发送验证码
        :param email:
        :return:
        """
        # 旧的状态置为-100
        code_by_db = AuthVerifyCode.query.filter_by(email=email, state=constants.VERIFY_CODE_ENABLE).first()
        if code_by_db:
            code_by_db.state = constants.VERIFY_CODE_DISABLE
            db.session.add(code_by_db)
            db.session.commit()

        # 获取新的验证码
        code = AuthVerifyCode.get_code(6)
        auth_verify_code = AuthVerifyCode(email=email, verify_code=code)
        send_email(email, code)
        db.session.add(auth_verify_code)
        db.session.commit()
