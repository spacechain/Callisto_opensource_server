# -*- coding: utf-8 -*-

from app import db
from app.models.tools import get_uuid
from datetime import datetime
import constants


class TransactionRecord(db.Model):
    """
    交易记录信息表
    """

    __tablename__ = 'transaction_records'

    id = db.Column(db.String(32), default=get_uuid, primary_key=True, unique=True, index=True, nullable=False)

    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'))

    # 是否需要延时24小时  10 是  -10 否
    delayed_type = db.Column(db.Integer, nullable=False, default=constants.WALLET_TYPE_NOT_DELAYED)

    # 压缩记录ID
    pack_id = db.Column(db.String(32), db.ForeignKey('pack_records.id'))

    # 未签名交易内容
    raw_tx_hex = db.Column(db.Text(), nullable=False)

    # 已签名交易内容(待广播交易)
    signed_tx_hex = db.Column(db.Text())

    # 状态值（待发送：10，已发送：20，广播成功：100，广播失败：-100,取消交易=-500，签名失败= -200)
    state = db.Column(db.Integer, nullable=False, default=constants.TRANSACTION_STATE_WAITING)

    payment_id = db.Column(db.String(132))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
