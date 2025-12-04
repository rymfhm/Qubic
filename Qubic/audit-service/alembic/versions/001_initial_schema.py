"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=True),
        sa.Column('step_index', sa.Integer(), nullable=True),
        sa.Column('step_type', sa.String(), nullable=True),
        sa.Column('input_hash', sa.String(), nullable=True),
        sa.Column('output_hash', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('qubic_txid', sa.String(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_task_id'), 'audit_logs', ['task_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_input_hash'), 'audit_logs', ['input_hash'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_input_hash'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_task_id'), table_name='audit_logs')
    op.drop_table('audit_logs')

