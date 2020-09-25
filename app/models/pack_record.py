# -*- coding: utf-8 -*-

from app import db
from app.models.tools import get_uuid
from datetime import datetime
import constants


class PackRecord(db.Model):
    """
    压缩记录 最多对应十条交易记录
    """
    __tablename__ = 'pack_records'

    id = db.Column(db.String(32), default=get_uuid, primary_key=True, nullable=False, index=True, unique=True)

    transaction_records = db.relationship('TransactionRecord', backref='pack_info')

    # 状态值（待发送：10，发送成功：20，发送失败：-20)
    state = db.Column(db.Integer, nullable=False,default=constants.PACK_STATE_WAITING)

    otp = db.Column(db.Integer, nullable=False)

    # 第几次压缩
    pack_index = db.Column(db.Integer, nullable=False)

    # 压缩完成后文件路径
    file_addr = db.Column(db.String(132), nullable=False, unique=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
