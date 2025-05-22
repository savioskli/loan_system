-- Add organization_id column to modules table
ALTER TABLE modules ADD COLUMN organization_id INT;
ALTER TABLE modules ADD CONSTRAINT fk_modules_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;
UPDATE modules SET organization_id = (SELECT id FROM organizations LIMIT 1);
ALTER TABLE modules MODIFY organization_id INT NOT NULL;

-- Add organization_id column to staff table
ALTER TABLE staff ADD COLUMN organization_id INT;
ALTER TABLE staff ADD CONSTRAINT fk_staff_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE;
UPDATE staff SET organization_id = (SELECT id FROM organizations LIMIT 1);
ALTER TABLE staff MODIFY organization_id INT NOT NULL;
