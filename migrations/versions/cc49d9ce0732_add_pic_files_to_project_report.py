"""add pic_files to project report

Revision ID: cc49d9ce0732
Revises: 90b229de33de
Create Date: 2017-04-29 21:39:09.882668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc49d9ce0732'
down_revision = '90b229de33de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project_reports', sa.Column('pic_files', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project_reports', 'pic_files')
    # ### end Alembic commands ###
