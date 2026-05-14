"""removed match_code from matches table

Revision ID: ddf5bbf90ecc
Revises: 81c2b4cc1208
Create Date: 2026-05-14 11:24:30.374041

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ddf5bbf90ecc"
down_revision = "81c2b4cc1208"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("matches", schema=None) as batch_op:
        batch_op.drop_column("match_code")


def downgrade():
    with op.batch_alter_table("matches", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("match_code", sa.String(length=64), nullable=True)
        )

    # ### end Alembic commands ###
