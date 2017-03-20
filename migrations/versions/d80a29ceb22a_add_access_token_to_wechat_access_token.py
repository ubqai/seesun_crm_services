"""add_access_token_to_wechat_access_token

Revision ID: d80a29ceb22a
Revises: 7939e3b94900
Create Date: 2017-03-02 09:54:28.650065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd80a29ceb22a'
down_revision = '7939e3b94900'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wechat_access_token', sa.Column('access_token', sa.String(length=500), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('wechat_access_token', 'access_token')
    # ### end Alembic commands ###