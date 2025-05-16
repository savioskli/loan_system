-- Cleanup script to truncate workflow history and reset loan impact records

-- First, truncate the workflow history table
TRUNCATE TABLE workflow_history;

-- Reset workflow instance ID in loan_impact table
UPDATE loan_impact SET workflow_instance_id = NULL, verification_status = 'Pending';

-- Truncate workflow instances table
TRUNCATE TABLE workflow_instances;

-- Truncate impact values and evidence
TRUNCATE TABLE impact_values;
TRUNCATE TABLE impact_evidence;

-- Truncate loan impact records
TRUNCATE TABLE loan_impact;

-- Show tables that were affected
SELECT 'workflow_history' AS table_name, COUNT(*) AS record_count FROM workflow_history
UNION
SELECT 'workflow_instances', COUNT(*) FROM workflow_instances
UNION
SELECT 'loan_impact', COUNT(*) FROM loan_impact
UNION
SELECT 'impact_values', COUNT(*) FROM impact_values
UNION
SELECT 'impact_evidence', COUNT(*) FROM impact_evidence;
