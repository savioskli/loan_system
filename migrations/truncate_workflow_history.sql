-- Truncate workflow history table
TRUNCATE TABLE workflow_history;

-- Reset workflow instance ID in loan_impact table
UPDATE loan_impact SET workflow_instance_id = NULL;

-- Truncate workflow instances table (this will remove all workflow instances)
TRUNCATE TABLE workflow_instances;
