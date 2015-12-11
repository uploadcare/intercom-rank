from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
project = Table('project', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=140)),
    Column('awis_access_id', String(length=140)),
    Column('awis_secret_access_key', String(length=140)),
    Column('intercom_app_id', String(length=140)),
    Column('intercom_app_api_key', String(length=140)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['project'].columns['awis_access_id'].create()
    post_meta.tables['project'].columns['awis_secret_access_key'].create()
    post_meta.tables['project'].columns['intercom_app_api_key'].create()
    post_meta.tables['project'].columns['intercom_app_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['project'].columns['awis_access_id'].drop()
    post_meta.tables['project'].columns['awis_secret_access_key'].drop()
    post_meta.tables['project'].columns['intercom_app_api_key'].drop()
    post_meta.tables['project'].columns['intercom_app_id'].drop()
