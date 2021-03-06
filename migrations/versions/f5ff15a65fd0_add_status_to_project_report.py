"""add status to project report

Revision ID: f5ff15a65fd0
Revises: 8a95ceb72160
Create Date: 2017-03-06 08:49:52.848479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5ff15a65fd0'
down_revision = '8a95ceb72160'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project_reports', sa.Column('status', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project_reports', 'status')
    # ### end Alembic commands ###
