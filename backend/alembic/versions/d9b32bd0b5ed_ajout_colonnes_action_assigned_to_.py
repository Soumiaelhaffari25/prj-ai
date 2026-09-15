"""ajout colonnes action (assigned_to, action_message)

Revision ID: d9b32bd0b5ed
Revises: a535a78ea0ff
Create Date: 2026-09-15 12:41:46.602140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd9b32bd0b5ed'
down_revision: Union[str, Sequence[str], None] = 'a535a78ea0ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('leads', sa.Column('assigned_to', sa.String(), nullable=True))
    op.add_column('leads', sa.Column('action_message', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('leads', 'action_message')
    op.drop_column('leads', 'assigned_to')
