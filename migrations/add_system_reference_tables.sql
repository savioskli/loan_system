-- Add system reference tables
BEGIN;

CREATE TABLE IF NOT EXISTS system_reference_fields (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_reference_values (
    id INT PRIMARY KEY AUTO_INCREMENT,
    field_id INT NOT NULL,
    value VARCHAR(255) NOT NULL,
    label VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    parent_value_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES system_reference_fields(id),
    FOREIGN KEY (parent_value_id) REFERENCES system_reference_values(id)
);

-- Add system reference field type to form_fields table
ALTER TABLE form_fields 
ADD COLUMN reference_field_code VARCHAR(50),
ADD COLUMN is_cascading BOOLEAN DEFAULT FALSE,
ADD COLUMN parent_field_id INT,
ADD FOREIGN KEY (parent_field_id) REFERENCES form_fields(id);

-- Insert some common system reference fields
INSERT INTO system_reference_fields (code, name, description) VALUES
('CLIENT_TYPE', 'Client Types', 'Types of clients in the system'),
('COUNTY', 'Counties', 'Counties in the system'),
('SUBCOUNTY', 'Sub Counties', 'Sub counties in the system'),
('STATUS', 'Status Definitions', 'Various status definitions');

COMMIT;
