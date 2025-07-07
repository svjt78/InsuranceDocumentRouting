"""create documents1 table

Revision ID: cfbad75dcfcd
Revises: 752de01f6b87
Create Date: 2025-06-30 00:14:36.989938

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfbad75dcfcd'
down_revision: Union[str, None] = '752de01f6b87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'documents1',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('s3_key', sa.String(), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('subcategory', sa.String(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('action_items', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('destination_bucket', sa.String(), nullable=True),
        sa.Column('destination_key', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('email_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                  server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), 
                  server_default=sa.func.now(), nullable=False),
        # New metadata fields:
        sa.Column('account_number',    sa.String(), nullable=True),
        sa.Column('policyholder_name', sa.String(), nullable=True),
        sa.Column('policy_number',     sa.String(), nullable=True),
        sa.Column('claim_number',      sa.String(), nullable=True),
    )
    # (Optional) add indexes if desired:
    op.create_index('ix_documents1_s3_key', 'documents1', ['s3_key'])


def downgrade():
    op.drop_table('documents1')
