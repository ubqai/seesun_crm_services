"""empty message

Revision ID: ea68faadfa4e
Revises: 3f632ce96098
Create Date: 2017-03-02 09:50:27.675113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea68faadfa4e'
down_revision = '3f632ce96098'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wechat_access_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('access_token', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('expires_in', sa.Integer(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('use_flag', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wechat_access_token')
    # ### end Alembic commands ###