"""add UniversityLink table

Revision ID: 57cb64d4adca
Revises: 69bc2d3b72b0
Create Date: 2022-08-31 16:56:59.975699

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '57cb64d4adca'
down_revision = '69bc2d3b72b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('universitylink',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('link', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_constraint('education_owner_id_fkey', 'education', type_='foreignkey')
    op.create_foreign_key(None, 'education', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('experience_owner_id_fkey', 'experience', type_='foreignkey')
    op.create_foreign_key(None, 'experience', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('profilephoto_owner_id_fkey', 'profilephoto', type_='foreignkey')
    op.create_foreign_key(None, 'profilephoto', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('userunilink_uni_id_fkey', 'userunilink', type_='foreignkey')
    op.drop_constraint('userunilink_user_id_fkey', 'userunilink', type_='foreignkey')
    op.create_foreign_key(None, 'userunilink', 'university', ['uni_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'userunilink', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'userunilink', type_='foreignkey')
    op.drop_constraint(None, 'userunilink', type_='foreignkey')
    op.create_foreign_key('userunilink_user_id_fkey', 'userunilink', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('userunilink_uni_id_fkey', 'userunilink', 'university', ['uni_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'profilephoto', type_='foreignkey')
    op.create_foreign_key('profilephoto_owner_id_fkey', 'profilephoto', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'experience', type_='foreignkey')
    op.create_foreign_key('experience_owner_id_fkey', 'experience', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'education', type_='foreignkey')
    op.create_foreign_key('education_owner_id_fkey', 'education', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
    op.drop_table('universitylink')
    # ### end Alembic commands ###
