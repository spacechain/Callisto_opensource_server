# -*- coding: utf-8 -*-

from app import db
from app.models.tools import get_uuid
from datetime import datetime
import constants


class ServerInfo(db.Model):
    """
    """
    __tablename__ = 'server_info'

    id = db.Column(db.String(32), default=get_uuid, primary_key=True, nullable=False, index=True, unique=True)

    sat_index = db.Column(db.Integer, nullable=False)

    # 100可用 -100禁用
    state = db.Column(db.Integer, nullable=False, default=constants.SERVER_ENABLE)
    # 记录初始化时的文件名称
    file_name = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
