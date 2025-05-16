-- Add workflow integration to loan_impact table
ALTER TABLE loan_impact
ADD COLUMN workflow_instance_id INT NULL,
ADD CONSTRAINT fk_loan_impact_workflow_instance FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(id);
