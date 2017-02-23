"""add buyer info to order

Revision ID: 0dcc2e844976
Revises: 7f5a5ea86cf3
Create Date: 2017-02-23 02:49:58.972707

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dcc2e844976'
down_revision = '7f5a5ea86cf3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('buyer_info', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'buyer_info')
    # ### end Alembic commands ###