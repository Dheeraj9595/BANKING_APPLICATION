"""Users id made string

Revision ID: 00dc8ba6179d
Revises: 
Create Date: 2024-02-22 11:38:24.245669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '00dc8ba6179d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'id',
               existing_type=mysql.INTEGER(),
               type_=sa.String(length=20),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'id',
               existing_type=sa.String(length=20),
               type_=mysql.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###