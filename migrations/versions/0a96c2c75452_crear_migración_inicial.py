"""Crear migración inicial

Revision ID: 0a96c2c75452
Revises: 
Create Date: 2024-10-12 08:16:06.943805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a96c2c75452'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reservation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reservation_rent_price', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('reservation_minimum_deposit', sa.Float(), nullable=True))
        batch_op.alter_column('reservation_total_amount',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.alter_column('reservation_deposit_amount',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.alter_column('start_date',
               existing_type=sa.DATETIME(),
               nullable=False)
        batch_op.alter_column('end_date',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reservation', schema=None) as batch_op:
        batch_op.alter_column('end_date',
               existing_type=sa.DATETIME(),
               nullable=True)
        batch_op.alter_column('start_date',
               existing_type=sa.DATETIME(),
               nullable=True)
        batch_op.alter_column('reservation_deposit_amount',
               existing_type=sa.FLOAT(),
               nullable=False)
        batch_op.alter_column('reservation_total_amount',
               existing_type=sa.FLOAT(),
               nullable=False)
        batch_op.drop_column('reservation_minimum_deposit')
        batch_op.drop_column('reservation_rent_price')

    # ### end Alembic commands ###
