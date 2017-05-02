"""merge migration conflict

Revision ID: 2d1bf125618d
Revises: 2ac2afb55e48, fc7fc4b255d1
Create Date: 2017-05-02 11:20:39.332592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d1bf125618d'
down_revision = ('2ac2afb55e48', 'fc7fc4b255d1')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
