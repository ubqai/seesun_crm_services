"""change production_num to float

Revision ID: fc7fc4b255d1
Revises: 0c39d2c5df1c
Create Date: 2017-05-02 10:27:16.805804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc7fc4b255d1'
down_revision = '0c39d2c5df1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('order_contents', 'production_num',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('order_contents', 'production_num',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # ### end Alembic commands ###
