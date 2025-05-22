BEGIN;

-- Add default modules if they don't exist, associating them with organization ID 1
INSERT INTO modules (name, code, description, is_system, organization_id, created_at, updated_at)
SELECT 
    'Client Management' as name,
    'CLT_MGT' as code,
    'Core module for managing client information and relationships' as description,
    1 as is_system,
    1 as organization_id,
    NOW() as created_at,
    NOW() as updated_at
WHERE NOT EXISTS (
    SELECT 1 FROM modules WHERE code = 'CLT_MGT'
);

INSERT INTO modules (name, code, description, is_system, organization_id, created_at, updated_at)
SELECT 
    'Loan Management' as name,
    'LN_MGT' as code,
    'Core module for managing loan processes and data' as description,
    1 as is_system,
    1 as organization_id,
    NOW() as created_at,
    NOW() as updated_at
WHERE NOT EXISTS (
    SELECT 1 FROM modules WHERE code = 'LN_MGT'
);

COMMIT;
