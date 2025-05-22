BEGIN;

-- Add default modules if they don't exist
INSERT IGNORE INTO modules (name, code, description, is_system, created_at, updated_at)
VALUES 
('Client Management', 'CLT_MGT', 'Core module for managing client information and relationships', 1, NOW(), NOW()),
('Loan Management', 'LN_MGT', 'Core module for managing loan processes and data', 1, NOW(), NOW());

COMMIT;
