"""create message_outbox table

Revision ID: 4a498c2044a5
Revises: cfbad75dcfcd
Create Date: 2025-07-04 01:05:54.277630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4a498c2044a5'
down_revision: Union[str, None] = 'cfbad75dcfcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'message_outbox',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('exchange', sa.String(), nullable=False),
        sa.Column('routing_key', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
    )
    # (you can also drop the explicit ix_message_outbox_id index if you like—
    # primary_key already creates one)

def downgrade() -> None:
    op.drop_table('message_outbox')

