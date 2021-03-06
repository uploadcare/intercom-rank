"""empty message

Revision ID: 50b85c2a8f04
Revises: None
Create Date: 2016-01-07 13:52:19.636773

"""

# revision identifiers, used by Alembic.
revision = '50b85c2a8f04'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.Unicode(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('reset_password_token', sa.String(length=100), nullable=False),
    sa.Column('is_enabled', sa.Boolean(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    ### end Alembic commands ###
