"""add material application model

Revision ID: ad50d4738049
Revises: c3b57fa131bc
Create Date: 2017-02-23 17:16:09.465503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad50d4738049'
down_revision = 'c3b57fa131bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('material_application',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('app_no', sa.String(length=30), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('app_no')
    )
    op.create_table('material_application_content',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('application_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['application_id'], ['material_application.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('material_application_content')
    op.drop_table('material_application')
    # ### end Alembic commands ###
