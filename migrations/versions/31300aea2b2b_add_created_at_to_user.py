"""add created_at to user

Revision ID: 31300aea2b2b
Revises: b96697ddd85b
Create Date: 2017-04-14 08:27:06.732804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31300aea2b2b'
down_revision = 'b96697ddd85b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    # ### end Alembic commands ###
