"""empty message

Revision ID: b5f9322993ee
Revises: 1dbe16b6add8
Create Date: 2016-11-13 20:12:25.436644

"""

# revision identifiers, used by Alembic.
revision = 'b5f9322993ee'
down_revision = '1dbe16b6add8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('destination_stats', sa.Column('bid_count', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('destination_stats', 'bid_count')
    ### end Alembic commands ###
