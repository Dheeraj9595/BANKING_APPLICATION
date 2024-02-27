"""abstract model updated for users

Revision ID: caacf513f383
Revises: b1985550d1c6
Create Date: 2024-02-26 19:05:58.711198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'caacf513f383'
down_revision: Union[str, None] = 'b1985550d1c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
