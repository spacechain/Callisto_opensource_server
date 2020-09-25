# -*- coding: utf-8 -*-

from struct import unpack
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import ftplib
import sys
import os

p_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(r'%s' % str(p_dir))

from config import config

# 初始化数据库连接:
engine = create_engine(config['default'].SQLALCHEMY_DATABASE_URI)
DBSession = sessionmaker(bind=engine)
session = DBSession()

# 下载下来的文件存储路径
file_local_path = config['default'].DOWNLOAD_FILE_PATH

# 测试网络中xpukey前缀
testnet_pubk_heads = ['tpub', 'tprv', 'upub', 'uprv', 'Upub', 'Uprv', 'vpub', 'vprv', 'Vpub', 'Vprv']


def check_file_name(names, logger):
    """
    剔除已经下载过的文件
    :param names:
    :return:
    """

    sql_str = """select file_name from server_info"""
    data_query = session.execute(sql_str)

    resuls = names
    session.close()

    for i in resuls:
        if i[-7:] != '.satpub':
            resuls.remove(i)
    logger.info('================file_list:%s ================' % ''.join(resuls))
    for record in data_query.fetchall():
        if record.file_name in resuls:
            resuls.remove(record.file_name)
    logger.info('================file_list:%s ================' % ''.join(resuls))

    return resuls


def ftp_download(logger):
    """
    ftp下载文件
    :return:
    """

    # FTP
    ftp_ip = config['default'].FTP_IP
    ftp_user = config['default'].FTP_USER
    ftp_pwd = config['default'].FTP_PWD
    ftp_path = config['default'].FTP_DOWNLOAD_PATH

    logger.info('================sign in ftp================')

    logger.info('====%s===========' % ftp_ip)
    logger.info('====%s===========' % ftp_user)
    logger.info('====%s===========' % ftp_pwd)
    logger.info('====%s===========' % ftp_path)

    f = ftplib.FTP(ftp_ip)  # 实例化FTP对象
    f.login(ftp_user, ftp_pwd)  # 登录
    f.cwd(ftp_path)

    # 总是提示链接超时
    f.set_pasv(True)
    # 获取当前路径
    file_list = f.nlst()

    if not file_list:
        logger.info('================ not file_list ================')

        return

    file_list = check_file_name(file_list, logger)
    if not file_list:
        session.close()
        return

    # 每次只下载一个初始化文件
    file_name = file_list[-1]
    logger.info('================ file name : %s ================' % file_name)

    fp = open(file_local_path + file_name, 'wb')
    f.retrbinary('RETR %s' % file_name, fp.write)
    fp.close()
    f.quit()

    return file_name


def init_server(logger):
    ftp_file_name = ftp_download(logger)
    if not ftp_file_name:
        return False

    logger.info('================ ftp_download down ================')

    f = open(file_local_path + ftp_file_name, 'rb')
    bf = f.read()
    f.close()

    server_id = bf[32:36]
    server_id = unpack('I', server_id)[0]

    logger.info('================ update state  ================')
    # 更改旧信息状态
    update_sql_str = """ update server_info set state = -100"""

    data_query = session.execute(update_sql_str)

    session.commit()
    logger.info('================ uuid.uuid4().hex %s  ================' % uuid.uuid4().hex)
    logger.info('================ server_id %s  ================' % server_id)
    logger.info('================ ftp_file_name %s  ================' % ftp_file_name)

    sql_str = '''insert into server_info(id,sat_index,created_at,updated_at,file_name,state) values ('%s',%s,'%s','%s','%s',100)''' % (
    uuid.uuid4().hex, server_id, datetime.utcnow(), datetime.utcnow(), ftp_file_name)

    data_query = session.execute(sql_str)
    session.commit()
    logger.info('================ insert to server_info  ================')

    pubkey_list = []

    pubkey_bytes = bf[36:]
    for i in range(1, 11):

        # 前两位是PUBKEY_INDEX
        pubkey_index = unpack('H', pubkey_bytes[:2])[0]

        # 获取PUBKEY_LEN
        pubkey_len = unpack('I', pubkey_bytes[2:6])[0]

        pubkey = unpack('%ss' % pubkey_len, pubkey_bytes[6:6 + pubkey_len])
        is_test = 0
        if pubkey[0:4] in testnet_pubk_heads:
            is_test = 1

        pubkey_item = {
            'index': pubkey_index,
            'key': pubkey
        }

        pubkey_bytes = pubkey_bytes[2 + 4 + pubkey_len:]

        pubkey_list.append(pubkey_item)

    for i in pubkey_list:
        new_id = uuid.uuid4().hex
        sql_str = '''insert into sat_xpub(id,xpub,sat_index,state,is_testnet,created_at,updated_at) values ('%s','%s',%s,100,%s,'%s','%s')''' % (
            new_id, str(i['key'][0], encoding="utf8"), i['index'], is_test, datetime.utcnow(), datetime.utcnow())
        data_query = session.execute(sql_str)
        session.commit()
