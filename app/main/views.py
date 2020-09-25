# -*- coding: utf-8 -*-

from flask import render_template, request
from app.main import main
from app.main.forms import OTPForm, InitForm
from flask_login import login_required
from flask import flash
from app.models import TransactionRecord, ServerInfo, PackRecord
from app import db
from crontab.pack import send_file
from crontab.unpack_certificate import init_server
from datetime import datetime, timedelta
from app.tools import ftp_upload
from app.tools import get_logger
import constants

logger = get_logger(__name__)


@main.before_request
def create_before_request():
    if request.method == 'GET':
        logger.info(request.args)
    elif request.method == 'POST':
        logger.info(request.form)


@main.route('/')
@login_required
def home():
    return render_template('base.html')


@main.route('/index')
@login_required
def index():
    # 最新的五次压缩记录都是OTP错误 则提醒更新OTP
    pack_list = PackRecord.query.limit(5)
    for pack_record in pack_list:
        if pack_record.state != constants.PULL_STATE_OTP_FAIL:
            return render_template('base.html')

    # 必须满足五次才提醒更新
    if len(list(pack_list)) == 5:
        flash('The OTP Secret key has been wrong five times, please change it..')

    return render_template('base.html')


@main.route('/pack_file', methods=['POST', 'GET'])
@login_required
def pack_file():
    """
    压缩文件
    :return:
    """
    form = OTPForm()
    befor_24 = datetime.utcnow() - timedelta(hours=constants.DELAYED_PERIOD)

    filter_by_dont_delay = '''(state =%s and delayed_type =%s )''' % (
        constants.TRANSACTION_STATE_WAITING, constants.WALLET_TYPE_NOT_DELAYED)

    filter_by_delay = '''(state = %s and delayed_type = %s and created_at <= '%s') ''' % (
        constants.TRANSACTION_STATE_WAITING, constants.WALLET_TYPE_DELAYED, befor_24)

    sql_str = '''select * from transaction_records where ''' + filter_by_dont_delay + ''' or ''' + \
              filter_by_delay + ''' order by  transaction_records.created_at  limit %s ''' % constants.PACK_NUM

    data_query = db.session.execute(sql_str)

    server_info = ServerInfo.query.filter_by(state=constants.SERVER_ENABLE).first()
    if not server_info:
        return render_template('base.html', m='Please initialize the server first')

    secret_id = server_info.sat_index

    if not data_query.fetchall():
        return render_template('base.html', m='No compression required')

    if form.validate_on_submit():
        otp = form.otp.data

        try:
            f_name = send_file(otp, logger, int(secret_id))
            ftp_upload(f_name)
        except Exception as e:
            logger.info('===============================================pack error %s' % str(e))
            return render_template('base.html', m=str(e))

        return render_template('base.html', m='Wait for satellite return')

    return render_template('pack_file.html', form=form)


@main.route('/initialize_server', methods=['POST', 'GET'])
@login_required
def initialize_server():
    form = InitForm()

    if form.validate_on_submit():

        try:
            if init_server(logger) is False:
                return render_template('base.html', m='Failure  initialization')

        except Exception as e:
            logger.info('===============================================pack error %s' % str(e))
            return render_template('base.html', m=str(e))

        return render_template('base.html', m='Successful initialization')

    return render_template('init_server.html', form=form)
