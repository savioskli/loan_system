-- Create system reference values table
BEGIN;

CREATE TABLE IF NOT EXISTS system_reference_values (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reference_field_code VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL,
    label VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ref_field_code (reference_field_code),
    INDEX idx_value (value),
    INDEX idx_is_active (is_active)
);

-- Insert initial client types
INSERT INTO system_reference_values 
(reference_field_code, value, label, description, is_active)
VALUES
('CLIENT_TYPE', 'individual', 'Individual', 'Individual client type', TRUE),
('CLIENT_TYPE', 'corporate', 'Corporate', 'Corporate/Business client type', TRUE),
('CLIENT_TYPE', 'group', 'Group', 'Group/Association client type', TRUE);

COMMIT;
