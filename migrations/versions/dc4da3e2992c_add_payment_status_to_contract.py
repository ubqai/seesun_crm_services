"""add payment_status to contract

Revision ID: dc4da3e2992c
Revises: e32af8c8d78a
Create Date: 2017-03-16 22:26:20.183651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc4da3e2992c'
down_revision = 'e32af8c8d78a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contracts', sa.Column('payment_status', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contracts', 'payment_status')
    # ### end Alembic commands ###
