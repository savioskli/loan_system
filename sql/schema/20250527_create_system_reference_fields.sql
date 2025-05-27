BEGIN;

CREATE TABLE IF NOT EXISTS system_reference_fields (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    field_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert some common system reference fields
INSERT INTO system_reference_fields (name, description, field_type) VALUES
('Member ID', 'Unique identifier for members', 'text'),
('Loan ID', 'Unique identifier for loans', 'text'),
('Account Number', 'Member account number', 'text'),
('Branch Code', 'Branch identifier code', 'text'),
('Transaction ID', 'Unique identifier for transactions', 'text');

COMMIT;
