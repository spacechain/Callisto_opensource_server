# -*- coding: utf-8 -*-

EOYDVGJ = ''  # 存在于注册时的邮箱内
WCTSIGB = ''  # 存在于注册时的邮箱内

# 将以下修改为你的邮箱信息，请确保你的邮箱已经开启POP/IMAP服务，该邮箱用于给用户发送"取消交易"等系统邮件
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USERNAME = ""  # 邮箱地址
MAIL_PASSWORD = ""  # 填写在“邮箱开通POP/IMAP服务”步骤中生成的密码

# 将以下修改为你的收费钱包XPUB，该信息作用于用户进行转账时对用户进行收取小费的功能
# 测试环境收费钱包XPUB
FEE_XPUB_BY_TESTNET = 'tpubD6NzVbkrYhZ4YsUnPYBtM1hy5hDo6m8q5jDPWBDhFXuizj6tFS7sD9kqPA7Cya3JBdxiwMZmTRd1axjtfKiSN59pUWEQbfCJ6bzP5rZSd8D'
# 主网环境收费钱包XPUB
FEE_XPUB = 'xpub661MyMwAqRbcH4XFkPVnQcG1jL6otSAAePud1yA2ZrKdBq15G7mqUFj9H7ijTGJTA7C7yKjsXcjarMRGvgV71iYzbhFJGUSjAsftdACRQLq'


# 连接数据库 将下面‘0.0.0.0’修改为当前环境下你自己的IP
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://mysqlaccount:qazwer1122@0.0.0.0:3306/TC'