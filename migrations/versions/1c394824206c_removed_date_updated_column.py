"""removed date_updated column

Revision ID: 1c394824206c
Revises: 2ecc3072cd2e
Create Date: 2025-01-14 02:58:22.998108

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c394824206c'
down_revision = '2ecc3072cd2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('date_updated')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_updated', sa.DATETIME(), nullable=False))

    # ### end Alembic commands ###
