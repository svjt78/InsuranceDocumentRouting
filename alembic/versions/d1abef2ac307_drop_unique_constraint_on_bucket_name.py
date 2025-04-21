"""drop unique constraint on bucket_name

Revision ID: d1abef2ac307
Revises: 7c32de80124d
Create Date: 2025-04-20 23:58:25.931899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1abef2ac307'
down_revision: Union[str, None] = '7c32de80124d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# replace with the real constraint name you discovered
CONSTRAINT_NAME = "bucket_mappings_bucket_name_key"  

def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(CONSTRAINT_NAME, "bucket_mappings", type_="unique")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint(CONSTRAINT_NAME, "bucket_mappings", ["bucket_name"])
