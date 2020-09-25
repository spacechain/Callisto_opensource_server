# -*- coding: utf-8 -*-

from app import create_app
from app import db
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from app.models import User, AuthVerifyCode, Wallet, PackRecord, TransactionRecord, PullRecord, SatXpub, ServerInfo

config_name = 'default'

app = create_app(config_name)
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
