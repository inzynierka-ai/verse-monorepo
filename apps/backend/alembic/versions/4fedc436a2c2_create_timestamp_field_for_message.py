"""Create timestamp field for message

Revision ID: ć
Revises: 
Create Date: 2025-02-25 23:43:00.714039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '4fedc436a2c2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define the default timestamp value
default_timestamp = datetime(2025, 1, 1, 0, 0)

def upgrade():
    # Step 1: Add the column as nullable
    op.add_column('messages', sa.Column('timestamp', sa.TIMESTAMP(), nullable=True))

    # Step 2: Backfill existing rows with the default timestamp
    messages_table = table('messages', column('timestamp', sa.TIMESTAMP()))
    op.execute(messages_table.update().values(timestamp=default_timestamp))

    # Step 3: Alter column to be non-nullable
    op.alter_column('messages', 'timestamp', nullable=False)


def downgrade():
    # Remove the column in case of downgrade
    op.drop_column('messages', 'timestamp')