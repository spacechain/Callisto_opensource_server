# -*- coding: utf-8 -*-
from struct import *
import ftplib
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import requests
import logging

p_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(r'%s' % str(p_dir))
from config import config
import constants
from bip32.transaction import Transaction



class DBExecute:

    def __init__(self, engine_path):
        # 创建引擎
        engine = create_engine(engine_path)
        # 创建会话通道
        DBsession = sessionmaker(bind=engine)
        self.session = DBsession()

    def execute(self, sql_str):
        """
        执行SQL语句
        :param sql_str: SQL语句
        :return:
        """
        self.session.execute(sql_str)
        self.session.commit()
        self.close()

    def query(self, sql_str):
        """
        执行查询语句 并返回查询结果
        :param sql_str:
        :return:
        """
        result = self.session.execute(sql_str)
        self.close()
        return result

    def close(self):
        """
        关闭会话通道
        :return:
        """
        self.session.close()


def get_logger():
    """
    logger初始化
    :return:
    """
    log_level = logging.DEBUG
    log_filemode = 'a'
    log_file_path = '/home/tc/server_log/unpack.log'
    log_format = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    logging.basicConfig(level=log_level, filename=log_file_path, filemode=log_filemode, format=log_format)
    return logging.getLogger(__name__)


def get_fee(tx_obj, billing_addr):
    """
    获取缴费记录
    :param tx_obj:
    :param billing_addr:
    :return:
    """

    outputs = {}
    for output in tx_obj.outputs():
        outputs[output[1]] = output[2]
    logger.info('================== outputs :%s =================' % str(outputs))

    if billing_addr in outputs and float(outputs[billing_addr]) == constants.FEE:
        return True
    return False


def check_file_name(names):
    """
    剔除已经下载过的文件
    :param names:
    :return:
    """
    logger.info('================== check_file_name =================')

    sql_str = """select file_names from pull_records"""

    data_query = db.query(sql_str)

    results = []

    # 确定是交易文件
    for name in names:
        if name[-4:] == '.res':
            results.append(name)

    # 剔除下载过的交易文件
    for record in data_query.fetchall():
        if record.file_names in results:
            results.remove(record.file_names)

    # 删除OTP错误超过五次之后的所有压缩文件
    sql_str = """ select file_addr  from pack_records where state = %s""" % constants.PULL_STATE_OTP_FAIL
    data_query = db.query(sql_str)
    for otp_error_record in data_query.fetchall():
        otp_error_name = otp_error_record.file_addr[0:-3] + ".res"
        if otp_error_name in results:
            results.remove(otp_error_name)

    logger.info('================== check_file_name result:%s =================' % ','.join(results))
    return results


def ftp_download():
    """
    ftp下载文件
    :return:
    """
    logger.info('================== ftp_download =================')

    ftp_ip = config['default'].FTP_IP
    ftp_user = config['default'].FTP_USER
    ftp_pwd = config['default'].FTP_PWD

    # FTP登录
    f = ftplib.FTP(ftp_ip)
    f.login(ftp_user, ftp_pwd)
    f.set_pasv(True)

    # 获取当前路径
    ftp_path = config['default'].FTP_DOWNLOAD_PATH
    f.cwd(ftp_path)
    logger.info('================== ftp_path =================%s' % ftp_path)

    # 获取当前文件夹下所有文件名称
    file_list = f.nlst()
    if not file_list:
        logger.info('================== not found files =================')
        exit()

    file_list = check_file_name(file_list)

    if not file_list:
        logger.info('================== No undownloaded files =================')
        exit()

    # 每次只下载一个签名文件
    file_name = file_list[0]
    # 下载下来的文件存储路径
    file_local_path = config['default'].DOWNLOAD_FILE_PATH
    # 保存文件
    fp = open(file_local_path + file_name, 'wb')
    f.retrbinary('RETR %s' % file_name, fp.write)
    fp.close()
    f.quit()

    # 入库下载记录
    new_id = uuid.uuid4().hex
    sql_str = '''insert into pull_records(id,state,file_names,created_at,updated_at) values ('%s',%s,'%s','%s','%s')''' % (
        new_id, constants.PULL_STATE_SUCCESS, file_name, datetime.utcnow(), datetime.utcnow())
    db.execute(sql_str)
    logger.info('==================insert pull_records =================%s' % new_id)

    return file_local_path + file_name, new_id


def otp_error_processing_mechanism(file_name):
    """
    otp错误后的处理机制
    :param file_name:
    :return:
    """
    file_addr = file_name.replace('.res', '.tx')
    file_addr = file_addr.split('/')[-1]
    pack_info_sql = """select * from pack_records where file_addr = '%s' """ % file_addr
    data_query = db.query(pack_info_sql)
    pack_info = data_query.fetchall()[0]

    pack_index = pack_info.pack_index
    # 前4次压缩
    pack_error_list = [pack_index - i for i in range(0, 5)]
    otp_error_sql = """select * from otp_error_record where pack_index in %s""" % str(tuple(pack_error_list))
    data_query = db.query(otp_error_sql)
    otp_error_list = data_query.fetchall()

    #  不够五次则只释放当前压缩下的交易记录
    if len(otp_error_list) != 5:
        # 修改该压缩记录下所有交易状态 置为待上传
        update_sql_str = """ update transaction_records set state = %s where pack_id = '%s' """ % (
            constants.TRANSACTION_STATE_WAITING, pack_info.id)

        db.execute(update_sql_str)

        # otp_error_record 插入当前错误信息
        sql_str = '''insert into otp_error_record(id,pack_index,pack_id,created_at,updated_at) values ('%s',%s,'%s','%s','%s')''' % (
            uuid.uuid4().hex, pack_info.pack_index, pack_info.id, datetime.utcnow(), datetime.utcnow())
        db.execute(sql_str)

    else:
        # otp错误等于五次 查出这次压缩 以及之后的所有压缩记录 释放交易
        pack_infos_sql = """select id from pack_records where created_at >= %s""" % pack_info.created_at
        data_query = db.query(pack_infos_sql)

        pack_ids = [i.id for i in data_query.fetchall()]

        # 修改该压缩记录下所有交易状态 置为待上传
        update_sql_str = """ update transaction_records set state = %s where pack_id in %s """ % (
            constants.TRANSACTION_STATE_WAITING, str(tuple(pack_ids)))

        db.execute(update_sql_str)

        # 所有之后的压缩记录 状态修改为OTP错误
        update_sql_str = """ update pack_records set sate = %s where  id in %s""" % (
            constants.PULL_STATE_OTP_FAIL, str(tuple(pack_ids)))
        db.execute(update_sql_str)


def change_pull_state(file_name, pull_id):
    """
    解压下载成功的文件 更改下载记录的解压状态
    :param file_name:
    :param pull_id:
    :return:
    """
    logger.info('================== change pull_records state =================%s' % pull_id)

    results = []
    try:
        results, state = unpack_file(file_name)

        if state == constants.PULL_STATE_OTP_FAIL:
            # otp失败后的处理机制
            logger.info('================== otp error =================%s')
            otp_error_processing_mechanism(file_name)

        elif state == constants.PULL_STATE_SERVER_ERROR:
            #  todo server_id错误后的处理机制
            logger.info('================== server_id error =================%s')
            pass
        elif state == constants.PULL_STATE_NOT_FOUND_TX:
            # todo 没有发现交易文件的处理机制
            logger.info('================== not found tx =================%s')
            pass

        sql_str = """ update pull_records set state = %s where id = '%s' """ % (state, str(pull_id))
    except:
        sql_str = """ update pull_records set state = %s where id = '%s' """ % (
            constants.PULL_STATE_UNPACK_FAIL, str(pull_id))
        logger.info('================== unpack_file error =================%s')

    db.execute(sql_str)
    logger.info('================== change pull_records state =================%s' % pull_id)

    return results


def get_tx_item(tx):
    """
    拆解每一个tx文件
    :param tx:
    :return:
    """
    tx_id = tx[0:32]
    tx_res_length = tx[32:36]

    tx_res_length = unpack('i', tx_res_length)

    # tx_res_data的长度
    tx_res_length = tx_res_length[0]

    # 板子签名失败
    if tx_res_length == 0:
        hex_data = None
    else:
        tx_res_data = tx[36:36 + tx_res_length]

        hex_data_len = tx_res_data[1:3]

        hex_data_len = unpack('H', hex_data_len)[0]

        hex_data = tx_res_data[3:3 + hex_data_len]

        hex_data = str(hex_data.hex())

    item_last_index = 36 + tx_res_length

    return tx_id, hex_data, item_last_index


def unpack_file(file_name):
    """
    解压文件
    :param file_name:
    :return:
    """

    logger.info('================== unpack_file =================%s' % file_name)

    f = open(file_name, "rb")
    f = f.read()

    server_id = f[0:4]
    server_id = unpack('i', server_id)[0]
    logger.info('================== server_id =================%s' % server_id)

    # 校验server_id
    sql_str = """select sat_index from server_info where state =%s""" % constants.SERVER_ENABLE
    data_query = db.query(sql_str)
    server_info = data_query.fetchall()[0]
    # server_id 错误
    if server_info.sat_index != server_id:
        logger.info('================== server_id error =================%s' % server_id)
        return None, constants.PULL_STATE_SERVER_ERROR

    tx_length = f[4:12]
    tx_length = unpack('q', tx_length)[0]

    tx_res_num = f[12:16]
    tx_res_num = unpack('i', tx_res_num)[0]

    # otp 验证失败 则每笔交易的长度为36
    if tx_res_num * 36 == tx_length:
        return None, constants.PULL_STATE_OTP_FAIL

    tx_list = f[16:16 + tx_length]

    results = []

    while True:

        if tx_list:
            tx_id, hex_data, item_last_index = get_tx_item(tx_list)

            results.append({
                'tx_id': tx_id,
                'hex': hex_data
            })
            tx_list = tx_list[item_last_index:]
        else:
            break

    # 没有发现交易文件
    if not results:
        return results, constants.PULL_STATE_NOT_FOUND_TX

    return results, constants.PULL_STATE_UNPACK_SUCCESS


def get_wallet_by_tx(tx_id):
    """
    根据交易ID查找对应钱包
    :param tx_id:
    :return:
    """
    find_tx_sql_str = """ select wallet_id from transaction_records where id = '%s' """ % tx_id

    data_query = db.query(find_tx_sql_str)
    transaction = data_query.fetchall()
    if not transaction:
        logger.info('================== not found transaction =================%s' % tx_id)
        return

    wallet_id = transaction[0].wallet_id

    find_wallet_sql_str = """ select * from wallets where id = '%s' """ % wallet_id

    data_query = db.query(find_wallet_sql_str)

    wallets = data_query.fetchall()
    if not wallets:
        logger.info('================== not found wallet =================%s' % wallet_id)
        return

    return wallets[0]


def broadcast(tx_list):
    """
    循环处理每笔交易
    :param tx_list:
    :return:
    """
    logger.info('================== broadcast =================')

    for tx_item in tx_list:

        # 多签信息
        hex_str = tx_item['hex']
        # 钱包ID
        tx_id = tx_item['tx_id'].decode()

        # 获取钱包信息
        wallet_info = get_wallet_by_tx(tx_id)
        if not wallet_info:
            broadcast
            continue

        # 卫星签名失败
        if hex_str is None:
            # 修改交易状态为 签名失败
            logger.info('================== sign error =================%s' % tx_id)
            update_sql_str = """ update transaction_records set state = %s where id = '%s' """ % (
                constants.TRANSACTION_STATE_SIGN_FAIL, tx_id)
            db.execute(update_sql_str)

            # 修改交易对应的钱包 剩余交易次数
            tx_remaining = wallet_info.tx_remaining + 1
            update_sql_str = """ update wallet set tx_remaining = %s where id = '%s' """ % (
                tx_remaining, wallet_info.id)
            db.execute(update_sql_str)
            logger.info('================== sign error ,change tx_remaining =================')
            # todo 发送邮件
            continue

        try:
            tx_obj = Transaction(hex_str)

            if not get_fee(tx_obj, wallet_info.billing_address):
                logger.info('================== no fee ,wallet id :%s =================' % wallet_info.id)
                continue

            # 修改钱包交易次数
            if wallet_info.tx_remaining < 0:

                if not get_fee(tx_obj, wallet_info.billing_address):
                    logger.info('================== no fee ,wallet id :%s =================' % wallet_info.id)
                    continue

                tx_remaining = wallet_info.tx_remaining + constants.INITIAL_RESIDUAL_NUMBER
                update_sql_str = """ update wallets set tx_remaining = %s where id = '%s' """ % (
                    tx_remaining, wallet_info.id)
                db.execute(update_sql_str)
                logger.info('================== change tx_remaining =================')

            logger.info('================== broadcast %s =================' % hex_str)
            b = requests.post("https://blockchain.info/pushtx", {'tx': hex_str})

            payment_id = tx_obj.txid()
            logger.info('================== payment_id ========%s=========' % payment_id)

        except Exception as e:
            # 广播失败
            logger.info('================== broadcast error =================')
            update_sql_str = """ update transaction_records set state = % where id = '%s' """ % (
                constants.TRANSACTION_STATE_BROADCAST_FAIL, tx_id)
            db.execute(update_sql_str)
            # todo 发送邮件
        else:

            # 广播成功
            update_sql_str = """ update transaction_records set signed_tx_hex = '%s' ,state = %d,payment_id='%s' where id = '%s' """ % (
                hex_str, constants.TRANSACTION_STATE_BROADCAST_SUCCESS, payment_id, tx_id)
            db.execute(update_sql_str)
            logger.info('================== broadcast down =================')


if __name__ == '__main__':
    db = DBExecute(config['default'].SQLALCHEMY_DATABASE_URI)
    logger = get_logger()

    file_path, pull_id = ftp_download()
    tx_list = change_pull_state(file_path, pull_id)

    if not tx_list:
        exit()

    broadcast(tx_list)

