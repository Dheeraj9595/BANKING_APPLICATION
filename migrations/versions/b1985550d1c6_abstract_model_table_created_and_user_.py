"""abstract model table created and user tabel inherited with abstract table

Revision ID: b1985550d1c6
Revises: 64d312800892
Create Date: 2024-02-26 19:02:33.589323

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1985550d1c6'
down_revision: Union[str, None] = '64d312800892'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
