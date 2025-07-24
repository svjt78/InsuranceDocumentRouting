"""add indexes to documents1.account_number, policy_number, claim_number

Revision ID: a8c3b191b682
Revises: 4a498c2044a5
Create Date: 2025-07-22 21:57:36.826534

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'a8c3b191b682'
down_revision: Union[str, None] = '4a498c2044a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add indexes to documents1."""
    op.create_index(
        'ix_documents1_account_number',
        'documents1',
        ['account_number'],
        unique=False
    )
    op.create_index(
        'ix_documents1_policy_number',
        'documents1',
        ['policy_number'],
        unique=False
    )
    op.create_index(
        'ix_documents1_claim_number',
        'documents1',
        ['claim_number'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema: drop indexes from documents1."""
    op.drop_index('ix_documents1_claim_number', table_name='documents1')
    op.drop_index('ix_documents1_policy_number', table_name='documents1')
    op.drop_index('ix_documents1_account_number', table_name='documents1')
