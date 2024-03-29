"""add_role_and_public_fields

Revision ID: d07fc8c41795
Revises: 57cb64d4adca
Create Date: 2022-09-03 16:15:54.191716

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'd07fc8c41795'
down_revision = '57cb64d4adca'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('public', sa.Boolean(), nullable=False, server_default="False"))
    op.add_column('user', sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default="user"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role')
    op.drop_column('user', 'public')
    # ### end Alembic commands ###
