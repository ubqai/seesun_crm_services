"""add timestamps to project report

Revision ID: c0778ba000bb
Revises: f5ff15a65fd0
Create Date: 2017-03-06 09:03:15.200570

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0778ba000bb'
down_revision = 'f5ff15a65fd0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project_reports', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('project_reports', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project_reports', 'updated_at')
    op.drop_column('project_reports', 'created_at')
    # ### end Alembic commands ###
