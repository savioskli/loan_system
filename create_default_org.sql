-- Create default organization
INSERT INTO organizations (name, code, description, is_active, created_at, updated_at)
VALUES ('Default Organization', 'ORG001', 'Default organization for the system', 1, NOW(), NOW());

-- Update modules table
UPDATE modules SET organization_id = (SELECT id FROM organizations WHERE code = 'ORG001') WHERE organization_id IS NULL;
ALTER TABLE modules MODIFY organization_id INT NOT NULL;

-- Update staff table
UPDATE staff SET organization_id = (SELECT id FROM organizations WHERE code = 'ORG001') WHERE organization_id IS NULL;
ALTER TABLE staff MODIFY organization_id INT NOT NULL;
