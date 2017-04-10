"""empty message

Revision ID: b96697ddd85b
Revises: cdc933dc3c56
Create Date: 2017-04-01 15:40:44.142760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b96697ddd85b'
down_revision = 'cdc933dc3c56'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('webpage_describes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('endpoint', sa.String(length=200), nullable=False),
    sa.Column('method', sa.String(length=4), nullable=True),
    sa.Column('describe', sa.String(length=200), nullable=False),
    sa.Column('validate_flag', sa.Boolean(), nullable=True),
    sa.Column('type', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('authority_operations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('webpage_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('flag', sa.String(length=10), nullable=True),
    sa.Column('remark', sa.String(length=200), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['webpage_id'], ['webpage_describes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('authority_operations')
    op.drop_table('webpage_describes')
    # ### end Alembic commands ###