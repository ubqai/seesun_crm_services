"""add category id to content

Revision ID: 0ad45412bffd
Revises: 8c795821d12d
Create Date: 2017-02-22 10:04:59.049118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ad45412bffd'
down_revision = '8c795821d12d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('content', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'content', 'content_category', ['category_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'content', type_='foreignkey')
    op.drop_column('content', 'category_id')
    # ### end Alembic commands ###
