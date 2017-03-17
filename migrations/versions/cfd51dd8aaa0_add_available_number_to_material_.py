"""add available number to material application

Revision ID: cfd51dd8aaa0
Revises: 9fea66319b4a
Create Date: 2017-03-16 17:42:49.960680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfd51dd8aaa0'
down_revision = 'dc4da3e2992c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('material_application_content', sa.Column('available_number', sa.Integer(), nullable=True))
    op.add_column('material_application_content', sa.Column('material_name', sa.String(length=100), nullable=True))
    op.drop_constraint('material_application_content_material_id_fkey', 'material_application_content', type_='foreignkey')
    op.drop_column('material_application_content', 'material_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('material_application_content', sa.Column('material_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('material_application_content_material_id_fkey', 'material_application_content', 'material', ['material_id'], ['id'])
    op.drop_column('material_application_content', 'material_name')
    op.drop_column('material_application_content', 'available_number')
    # ### end Alembic commands ###
