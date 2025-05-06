"""add_scene_summary_table

Revision ID: bfd70e4f42a5
Revises: ed406e43b542
Create Date: 2025-05-05 23:03:43.210647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfd70e4f42a5'
down_revision: Union[str, None] = 'ed406e43b542'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create scene_summaries table
    op.create_table(
        'scene_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scene_id', sa.Integer(), nullable=False),
        sa.Column('total_messages', sa.Integer(), nullable=False),
        sa.Column('character_participation', sa.JSON(), nullable=False),
        sa.Column('key_events', sa.JSON(), nullable=False),
        sa.Column('sentiment', sa.JSON(), nullable=False),
        sa.Column('relationships', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scene_id')
    )
    op.create_index(op.f('ix_scene_summaries_id'), 'scene_summaries', ['id'], unique=False)


def downgrade() -> None:
    # Drop scene_summaries table
    op.drop_index(op.f('ix_scene_summaries_id'), table_name='scene_summaries')
    op.drop_table('scene_summaries')
