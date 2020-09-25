# -*- coding: utf-8 -*-

from struct import *
from Crypto.Cipher import AES
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
import uuid
import time


def pkcs7padding(text):
    """
    明文使用PKCS7填充
    最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理
    :param text: 待加密内容(明文)
    :return:
    """
    bs = AES.block_size  # 16
    length = len(text)
    padding_size = length
    padding = bs - padding_size % bs
    padding_text = b'\0' * padding

    return text + padding_text


def pkcs7unpadding(text):
    """
    处理使用PKCS7填充过的数据
    :param text: 解密后的字符串
    :return:
    """
    length = len(text)
    unpadding = text[length - 1]
    return text[0:length - unpadding]


def encrypt(key, content):
    """
    AES加密
    key,iv使用同一个
    模式cbc
    填充pkcs7
    :param key: 密钥
    :param content: 加密内容
    :return:
    """
    key_bytes = bytes(key, encoding='utf-8')
    iv = key_bytes
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    # 处理明文
    content_padding = pkcs7padding(content)
    # 加密
    encrypt_bytes = cipher.encrypt(content_padding)
    # 重新编码
    result = encrypt_bytes
    return result


def decrypt(key, content):
    """
    AES解密
     key,iv使用同一个
    模式cbc
    去填充pkcs7
    :param key:
    :param content:
    :return:
    """
    key_bytes = bytes(key, encoding='utf-8')
    iv = key_bytes
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    encrypt_bytes = content
    # 解密
    decrypt_bytes = cipher.decrypt(encrypt_bytes)

    # 重新编码
    result = decrypt_bytes
    return result


def pack_item(x1, x2, sat_xpub_index, raw_tx, aes_key, transaction_id, logger):
    """

    :param x1: 用户公钥1
    :param x2: 用户公钥2
    :param sat_xpub_index:  卫星公钥ID
    :param raw_tx: 交易内容
    :param aes_key: 加密的秘钥OTP
    :param transaction_id: 数据库中交易ID
    :param logger:

    :return:
    """
    tx_head = b'\xa1'

    sat_xpub_index_head = b'\xba'
    xpub_index = pack('<H', sat_xpub_index)
    sat_xpub_index_len = pack('<H', len(xpub_index))

    hex_head = b'\xca'
    hex_str = bytes.fromhex(raw_tx)
    hex_str_len = len(hex_str)
    logger.info('=========hex_str_len=============%s' % str(hex_str_len))

    hex_str = pack('<%ss' % hex_str_len, hex_str)
    hex_str_len = pack('<h', len(hex_str))

    tx_end = b'\x1a'

    tx_data_down = sat_xpub_index_head + sat_xpub_index_len + xpub_index + hex_head + hex_str_len + hex_str + tx_end
    tx_data = tx_head + pack('<H', len(tx_data_down)) + tx_data_down

    logger.info('=========tx_data=============%s' % str(tx_data))

    encrypt_en = encrypt(aes_key, tx_data)

    tx_id = pack('<32s', bytes(transaction_id, encoding='utf8'))

    tx_data_len = pack('<I', len(encrypt_en))
    logger.info(('========= len(encrypt_en)=============%s' % str(len(encrypt_en))))
    one_tx = tx_id + tx_data_len + encrypt_en

    return one_tx


def pack_list(server_id, aes_key, transactions, pay_num, logger):
    """

    :param transactions: 加密完成后的交易
    :param server_id: 卫星分配给服务器的ID 99
    :param aes_key: 加密的秘钥OTP
    :param pay_num:
    :param logger:

    :return:
    """

    f_name = str(time.time()).replace('.', '')

    if len(f_name) < 17:
        f_name = f_name + (17 - len(f_name)) * '0'
    if len(f_name) > 17:
        f_name = f_name[0:17]

    file_name = '0' * (5 - (len(str(server_id)))) + str(server_id) + '-000' + f_name + '.tx'
    logger.info('=========pay_num=============%s' % str(pay_num))

    server_id = pack('<I', server_id)

    check_block = encrypt(aes_key, server_id)

    check_block = pack('<16s', check_block)

    logger.info('=========pay_num=============%s' % str(pay_num))
    pay_num = pack('<I', pay_num)
    logger.info('========= len(transactions))=============%s' % str(len(transactions)))

    result = server_id + check_block + pay_num + pack('<I', len(transactions)) + transactions

    f_path = config['default'].PACK_FILE_PATH + file_name
    f1 = open(f_path, 'wb')

    f1.write(result)
    f1.close()
    return file_name


def to_pack(otp, session, server_id, logger):
    """

    state == 10 and delayed_type = -10, 不用延时且待发送
    state == 10 and delayed_type = -10  now - created_at >=24h, 用延时 待发送 时间正确
    (state ==10 and delayed_type = -10 ) or (state == 10 and delayed_type = 10 and created_at <= befor_24)
    :param otp:
    :param session:
    :param server_id:
    :param logger:
    :return:
    """
    new_otp = str(otp) + '0000000000'

    befor_24 = datetime.utcnow() - timedelta(hours=24)

    sql_str = '''select * from sat_xpub,wallets,transaction_records where  transaction_records.wallet_id = wallets.id
   and wallets.sat_xpub_id = sat_xpub.id and ((transaction_records.state =10 and
    transaction_records.delayed_type = -10 ) or (transaction_records.state = 10 and 
    transaction_records.delayed_type = 10 and transaction_records.created_at <= '%s'))  
    order by  transaction_records.created_at  limit 10 ''' % befor_24

    data_query = session.execute(sql_str)

    transactions = b''

    transaction_ids = []
    for transaction in data_query.fetchall():
        transactions += pack_item(transaction.first_xpub, transaction.secondary_xpub, transaction.sat_index,
                                  transaction.raw_tx_hex, new_otp, transaction.id, logger)
        transaction_ids.append(transaction.id)

    return pack_list(server_id, new_otp, transactions, len(transaction_ids), logger), transaction_ids


def send_file(otp, logger, server_id):
    """

    :param otp:
    :param logger:
    :param server_id:
    :return:
    """
    # 初始化数据库连接:
    engine = create_engine(config['default'].SQLALCHEMY_DATABASE_URI)
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    f_name, transaction_ids = to_pack(otp, session, server_id, logger)
    new_id = uuid.uuid4().hex

    sql_str = """select * FROM pack_records ORDER BY created_at DESC LIMIT 0,1 """
    data_query = session.execute(sql_str)
    pack_record = data_query.fetchall()
    if len(pack_record) == 0:
        pack_index = 1
    else:
        pack_index = pack_record[0].pack_index + 1
    sql_str = '''insert into pack_records(id,pack_index,state,otp,file_addr,created_at,updated_at) values ('%s',%s,%s,%s,'%s','%s','%s')''' % (
        new_id, pack_index, 20, int(otp), f_name, datetime.utcnow(), datetime.utcnow())

    data_query = session.execute(sql_str)

    update_where_str = ''

    for i in transaction_ids:
        new_i = "'" + i + "',"
        update_where_str = update_where_str + new_i

    update_sql_str = """update transaction_records set state = 20,pack_id = '%s' where id in (%s)""" % (
        new_id, update_where_str[0:-1])
    data_query = session.execute(update_sql_str)
    session.commit()

    session.close()

    return f_name
