"""merge migration conflict

Revision ID: cdc933dc3c56
Revises: f96e60b9c39c, 636191448952
Create Date: 2017-03-29 14:13:45.698385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdc933dc3c56'
down_revision = ('f96e60b9c39c', '636191448952')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
