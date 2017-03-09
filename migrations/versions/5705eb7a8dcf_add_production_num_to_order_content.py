"""add production_num to order_content

Revision ID: 5705eb7a8dcf
Revises: c2024ad11427
Create Date: 2017-03-10 00:02:23.674172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5705eb7a8dcf'
down_revision = 'c2024ad11427'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_contents', sa.Column('inventory_choose', sa.JSON(), nullable=True))
    op.add_column('order_contents', sa.Column('production_num', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_contents', 'production_num')
    op.drop_column('order_contents', 'inventory_choose')
    # ### end Alembic commands ###