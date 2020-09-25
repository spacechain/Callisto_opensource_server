# -*- coding: utf-8 -*-

from app import db
from app.models.tools import get_uuid
from datetime import datetime


class PullRecord(db.Model):
    """
    拉取文件记录
    """
    __tablename__ = 'pull_records'

    id = db.Column(db.String(32), default=get_uuid, primary_key=True, nullable=False, index=True, unique=True)

    # 状态值（拉取成功 10，拉取失败 -10，解压成功 50，解压失败 -50 -100 OTP验证失败,-200 server——id错误)
    state = db.Column(db.Integer, nullable=False)
    # 拉取的所有文件的名称列表  "name1%name2%name3%name4"
    file_names = db.Column(db.String(256), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
