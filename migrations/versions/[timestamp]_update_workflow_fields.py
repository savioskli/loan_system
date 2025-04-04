"""Update workflow fields in collection_schedules"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add new columns
    op.add_column('collection_schedules', sa.Column('current_step_id', sa.Integer(), nullable=True))
    op.add_column('collection_schedules', sa.Column('workflow_instance_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraints
    op.create_foreign_key(
        'fk_collection_schedules_current_step_id',
        'collection_schedules', 'workflow_steps',
        ['current_step_id'], ['id']
    )
    op.create_foreign_key(
        'fk_collection_schedules_workflow_instance_id',
        'collection_schedules', 'workflow_instances',
        ['workflow_instance_id'], ['id']
    )
    
    # Drop old column
    if op.get_context().dialect.has_table(op.get_bind(), 'collection_schedules'):
        if op.get_context().dialect.has_column('collection_schedules', 'current_step'):
            op.drop_column('collection_schedules', 'current_step')


def downgrade():
    # Recreate old column
    op.add_column('collection_schedules', sa.Column('current_step', sa.Integer(), nullable=True))
    
    # Drop foreign key constraints
    op.drop_constraint('fk_collection_schedules_current_step_id', 'collection_schedules', type_='foreignkey')
    op.drop_constraint('fk_collection_schedules_workflow_instance_id', 'collection_schedules', type_='foreignkey')
    
    # Drop new columns
    op.drop_column('collection_schedules', 'current_step_id')
    op.drop_column('collection_schedules', 'workflow_instance_id')
