-- Migration: Create Corporate Client Tables
-- Created: 2025-06-20

-- Create table for corporate officials
CREATE TABLE IF NOT EXISTS corporate_officials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    id_number VARCHAR(50) NOT NULL,
    contact VARCHAR(50),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    organization_id INT,
    FOREIGN KEY (client_id) REFERENCES client_registration_data(id) ON DELETE CASCADE
);

-- Create table for corporate signatories
CREATE TABLE IF NOT EXISTS corporate_signatories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    id_number VARCHAR(50) NOT NULL,
    signature_level VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    organization_id INT,
    FOREIGN KEY (client_id) REFERENCES client_registration_data(id) ON DELETE CASCADE
);

-- Create table for corporate attachments
CREATE TABLE IF NOT EXISTS corporate_attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    organization_id INT,
    FOREIGN KEY (client_id) REFERENCES client_registration_data(id) ON DELETE CASCADE
);

-- Create table for corporate services
CREATE TABLE IF NOT EXISTS corporate_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    service_type INT,
    details TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    organization_id INT,
    FOREIGN KEY (client_id) REFERENCES client_registration_data(id) ON DELETE CASCADE,
    FOREIGN KEY (service_type) REFERENCES system_reference_values(id)
);

-- Add columns to form_sections table
ALTER TABLE form_sections 
ADD COLUMN is_repeatable BOOLEAN DEFAULT FALSE,
ADD COLUMN min_entries INT DEFAULT 0,
ADD COLUMN max_entries INT DEFAULT 0,
ADD COLUMN related_model VARCHAR(100);

-- Update the Officials section to be repeatable
UPDATE form_sections 
SET is_repeatable = TRUE, 
    min_entries = 1, 
    max_entries = 10, 
    related_model = 'CorporateOfficial'
WHERE name = 'Officials' AND module_id = 33;

-- Update the Signatories section to be repeatable
UPDATE form_sections 
SET is_repeatable = TRUE, 
    min_entries = 1, 
    max_entries = 5, 
    related_model = 'CorporateSignatory'
WHERE name = 'Signatories' AND module_id = 33;

-- Update the Corporate Documents section to be repeatable
UPDATE form_sections 
SET is_repeatable = TRUE, 
    min_entries = 0, 
    max_entries = 10, 
    related_model = 'CorporateAttachment'
WHERE name = 'Corporate Documents' AND module_id = 33;

-- Update the Services section to be repeatable
UPDATE form_sections 
SET is_repeatable = TRUE, 
    min_entries = 0, 
    max_entries = 10, 
    related_model = 'CorporateService'
WHERE name = 'Services' AND module_id = 33;
