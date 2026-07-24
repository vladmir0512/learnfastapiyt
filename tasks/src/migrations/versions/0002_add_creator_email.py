"""add creator_email to tasks

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-24

"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('tasks', sa.Column('creator_email', sa.String(), nullable=False, server_default=''))

def downgrade():
    op.drop_column('tasks', 'creator_email')
