"""Добавлено поле password

Revision ID: 1b822d07fafc
Revises: 2ded1a324fc3
Create Date: 2024-05-11 11:36:14.159908

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "1b822d07fafc"
down_revision = "2ded1a324fc3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("password", sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "password")
    # ### end Alembic commands ###
