"""add surname

Revision ID: 0bc7b93bc825
Revises: 85b6afb9e90e
Create Date: 2022-03-24 10:46:39.553964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bc7b93bc825'
down_revision = '85b6afb9e90e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('author_model', sa.Column('surname', sa.String(length=32), server_default='Иванов', nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('author_model', 'surname')
    # ### end Alembic commands ###