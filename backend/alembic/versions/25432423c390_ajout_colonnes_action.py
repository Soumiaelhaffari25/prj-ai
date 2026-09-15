"""ajout colonnes action

Revision ID: 25432423c390
Revises: d9b32bd0b5ed
Create Date: 2026-09-15 13:01:00.693230

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '25432423c390'
down_revision: Union[str, Sequence[str], None] = 'd9b32bd0b5ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
