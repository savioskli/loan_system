-- Add conditions column to workflow_transitions table
ALTER TABLE workflow_transitions ADD COLUMN conditions JSON DEFAULT NULL AFTER transition_name;
