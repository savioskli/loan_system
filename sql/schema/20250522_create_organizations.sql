BEGIN;

CREATE TABLE organizations (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

-- Add organization_id to modules table
ALTER TABLE modules ADD COLUMN organization_id INT;
ALTER TABLE modules ADD FOREIGN KEY (organization_id) REFERENCES organizations(id);

-- Add organization_id to form_fields table
ALTER TABLE form_fields ADD COLUMN organization_id INT;
ALTER TABLE form_fields ADD FOREIGN KEY (organization_id) REFERENCES organizations(id);

-- Add organization_id to staff table
ALTER TABLE staff ADD COLUMN organization_id INT;
ALTER TABLE staff ADD FOREIGN KEY (organization_id) REFERENCES organizations(id);

COMMIT;

-- Rollback in case of failure
-- ROLLBACK;
