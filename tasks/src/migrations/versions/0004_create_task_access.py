"""create task_access table

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-24

"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'task_access',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('task_id', 'user_id', name='uq_task_user_access'),
    )

def downgrade():
    op.drop_table('task_access')
