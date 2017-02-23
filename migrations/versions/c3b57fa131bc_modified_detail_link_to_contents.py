"""modified detail link to contents

Revision ID: c3b57fa131bc
Revises: 2372f1f8d894
Create Date: 2017-02-23 14:20:45.528242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3b57fa131bc'
down_revision = '2372f1f8d894'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('content', sa.Column('detail_link', sa.String(length=200), nullable=True))
    op.add_column('content', sa.Column('image_links', sa.JSON(), nullable=True))
    op.drop_column('content', 'image_path')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('content', sa.Column('image_path', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.drop_column('content', 'image_links')
    op.drop_column('content', 'detail_link')
    # ### end Alembic commands ###
