"""add audit price to share inventory

Revision ID: 636191448952
Revises: 0c451fc35b86
Create Date: 2017-03-29 11:04:56.305056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '636191448952'
down_revision = '0c451fc35b86'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('share_inventory', sa.Column('audit_price', sa.Float(), nullable=True))
    op.alter_column('web_access_log', 'user_agent',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.String(length=500),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('web_access_log', 'user_agent',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=200),
               existing_nullable=True)
    op.drop_column('share_inventory', 'audit_price')
    # ### end Alembic commands ###
