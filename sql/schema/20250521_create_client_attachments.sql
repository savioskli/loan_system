-- Create client attachments table
-- Date: 2025-05-21
-- Description: Adds table for managing client document requirements by client type

START TRANSACTION;

-- Create the table
CREATE TABLE IF NOT EXISTS client_attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_type_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    attachment_type VARCHAR(50) NOT NULL,
    size_limit INT,
    is_mandatory BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    FOREIGN KEY (client_type_id) REFERENCES client_types(id),
    FOREIGN KEY (created_by) REFERENCES staff(id),
    FOREIGN KEY (updated_by) REFERENCES staff(id),
    INDEX ix_client_attachments_client_type_id (client_type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

COMMIT;

-- Rollback script (if needed):
/*
START TRANSACTION;
DROP TABLE IF EXISTS client_attachments;
COMMIT;
*/
