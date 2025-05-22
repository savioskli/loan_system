-- Update modules table
UPDATE modules SET organization_id = (SELECT id FROM organizations LIMIT 1) WHERE organization_id IS NULL;
ALTER TABLE modules MODIFY organization_id INT NOT NULL;

-- Update staff table
UPDATE staff SET organization_id = (SELECT id FROM organizations LIMIT 1) WHERE organization_id IS NULL;
ALTER TABLE staff MODIFY organization_id INT NOT NULL;
