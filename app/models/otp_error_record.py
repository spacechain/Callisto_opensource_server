# -*- coding: utf-8 -*-

from app import db
from app.models.tools import get_uuid
from datetime import datetime


class OtpErrorRecord(db.Model):
    """
    压缩文件时 OTP错误记录
    """
    __tablename__ = 'otp_error_record'

    id = db.Column(db.String(32), default=get_uuid, primary_key=True, nullable=False, index=True, unique=True)

    # 第几次压缩
    pack_index = db.Column(db.Integer, unique=False)

    pack_id = db.Column(db.String(32), unique=False)

    file_name = db.Column(db.String(32), unique=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
