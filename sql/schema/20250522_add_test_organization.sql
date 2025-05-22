BEGIN;

INSERT INTO organizations (name, code, description, created_at, updated_at)
VALUES ('Test Organization', 'TEST001', 'Test organization for testing', NOW(), NOW());

COMMIT;
