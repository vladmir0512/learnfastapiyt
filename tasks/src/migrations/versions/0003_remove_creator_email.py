"""remove creator_email from tasks

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-24

"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('tasks', 'creator_email')

def downgrade():
    op.add_column('tasks', sa.Column('creator_email', sa.String(), nullable=False, server_default=''))
