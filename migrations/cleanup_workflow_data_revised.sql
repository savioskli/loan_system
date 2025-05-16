-- Revised cleanup script to delete workflow data while respecting foreign key constraints

-- First, delete workflow history records (child table)
DELETE FROM workflow_history;

-- Reset workflow instance ID in loan_impact table
UPDATE loan_impact SET workflow_instance_id = NULL, verification_status = 'Pending';

-- Delete workflow instances
DELETE FROM workflow_instances;

-- Delete impact values and evidence (child tables of loan_impact)
DELETE FROM impact_values;
DELETE FROM impact_evidence;

-- Delete loan impact records
DELETE FROM loan_impact;

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
