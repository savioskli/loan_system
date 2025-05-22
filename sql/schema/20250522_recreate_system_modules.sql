BEGIN;

-- Remove existing system modules
DELETE FROM modules WHERE is_system = 1;

-- Add default modules with organization_id=1
INSERT INTO modules (name, code, description, is_system, organization_id, is_active, created_at, updated_at)
VALUES 
('Client Management', 'CLT_MGT', 'Core module for managing client information and relationships', 1, 1, 1, NOW(), NOW()),
('Loan Management', 'LN_MGT', 'Core module for managing loan processes and data', 1, 1, 1, NOW(), NOW());

COMMIT;
