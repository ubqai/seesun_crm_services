"""empty message

Revision ID: e334c53b9bba
Revises: 901a4674cb12
Create Date: 2017-03-08 10:19:02.648204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e334c53b9bba'
down_revision = '901a4674cb12'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracking_info', sa.Column('delivery_man_name', sa.String(length=200), nullable=True))
    op.add_column('tracking_info', sa.Column('logistics_company', sa.String(length=200), nullable=True))
    op.add_column('tracking_info', sa.Column('production_ends_at', sa.DateTime(), nullable=True))
    op.add_column('tracking_info', sa.Column('production_manager', sa.String(length=200), nullable=True))
    op.add_column('tracking_info', sa.Column('production_starts_at', sa.DateTime(), nullable=True))
    op.add_column('tracking_info', sa.Column('qrcode_image', sa.String(length=200), nullable=True))
    op.add_column('tracking_info', sa.Column('qrcode_token', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tracking_info', 'qrcode_token')
    op.drop_column('tracking_info', 'qrcode_image')
    op.drop_column('tracking_info', 'production_starts_at')
    op.drop_column('tracking_info', 'production_manager')
    op.drop_column('tracking_info', 'production_ends_at')
    op.drop_column('tracking_info', 'logistics_company')
    op.drop_column('tracking_info', 'delivery_man_name')
    # ### end Alembic commands ###
