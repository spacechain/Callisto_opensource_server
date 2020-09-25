# -*- coding: utf-8 -*-

from app import db
from app.models.tools import get_uuid
from datetime import datetime
import constants


class SatXpub(db.Model):
    """
    卫星公钥信息
    """
    __tablename__ = 'sat_xpub'

    id = db.Column(db.String(32), default=get_uuid, primary_key=True, nullable=False, index=True, unique=True)

    xpub = db.Column(db.String(128), nullable=False)

    # 卫星下发的ID
    sat_index = db.Column(db.Integer, nullable=False)

    state = db.Column(db.Integer, default=constants.XPUB_STATE_ENABLE, nullable=False)

    wallets = db.relationship('Wallet', backref='sat_xpub_info')

    # 是否为测试网络，是：1 否：0
    is_testnet = db.Column(db.Integer(), nullable=False, default=constants.BITCOIN_MAIN)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
