-- Update existing form_fields to use the default organization
UPDATE form_fields SET organization_id = (SELECT id FROM organizations WHERE code = 'ORG001') WHERE organization_id IS NULL;
ALTER TABLE form_fields MODIFY organization_id INT NOT NULL;
