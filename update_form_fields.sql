-- Add organization_id column to form_fields table
ALTER TABLE form_fields ADD COLUMN organization_id INT;
ALTER TABLE form_fields ADD CONSTRAINT fk_form_fields_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;

-- Update existing form_fields to use the default organization
UPDATE form_fields SET organization_id = (SELECT id FROM organizations WHERE code = 'ORG001') WHERE organization_id IS NULL;
ALTER TABLE form_fields MODIFY organization_id INT NOT NULL;
