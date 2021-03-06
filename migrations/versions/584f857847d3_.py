"""empty message

Revision ID: 584f857847d3
Revises: 711edb75f173
Create Date: 2016-11-16 13:19:20.822128

"""

# revision identifiers, used by Alembic.
revision = '584f857847d3'
down_revision = '711edb75f173'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('add_airport',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('iata', sa.String(length=3), nullable=True),
    sa.Column('city_code', sa.String(length=3), nullable=True),
    sa.Column('city', sa.String(length=50), nullable=True),
    sa.Column('country_code', sa.String(length=3), nullable=True),
    sa.Column('country', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('add_airport')
    ### end Alembic commands ###
