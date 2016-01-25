"""Fill data about free email providers.

Revision ID: 86b9515e9096
Revises: ef6edca55d1d
Create Date: 2016-01-25 16:30:47.307419

"""

# revision identifiers, used by Alembic.
revision = '86b9515e9096'
down_revision = 'ef6edca55d1d'

from alembic import op
import sqlalchemy as sa
from app import FREE_EMAILS_SET, db
from app.accounts.models import FreeEmailProvider


def upgrade():
    CHUNK_SIZE = 1000

    for i, domain in enumerate(FREE_EMAILS_SET):
        if i and i % CHUNK_SIZE == 0:
            db.session.commit()
        db.session.add(FreeEmailProvider(domain=domain))


def downgrade():
    pass
