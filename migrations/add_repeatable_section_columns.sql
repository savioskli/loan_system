-- Migration to add repeatable section columns to form_sections table

-- Add is_repeatable column (boolean)
ALTER TABLE form_sections ADD COLUMN is_repeatable BOOLEAN DEFAULT FALSE;

-- Add min_entries column (integer)
ALTER TABLE form_sections ADD COLUMN min_entries INTEGER DEFAULT 0;

-- Add max_entries column (integer)
ALTER TABLE form_sections ADD COLUMN max_entries INTEGER DEFAULT 10;

-- Add related_model column (string)
ALTER TABLE form_sections ADD COLUMN related_model VARCHAR(100) NULL;

-- Update existing corporate sections to be repeatable
UPDATE form_sections 
SET is_repeatable = TRUE, 
    min_entries = 1, 
    max_entries = 10
WHERE name IN ('Officials', 'Signatories', 'Attachments', 'Services') 
  AND module_id = 33;  -- Assuming module_id 33 is for client registration

-- Set related_model for each repeatable section
UPDATE form_sections SET related_model = 'CorporateOfficial' WHERE name = 'Officials' AND module_id = 33;
UPDATE form_sections SET related_model = 'CorporateSignatory' WHERE name = 'Signatories' AND module_id = 33;
UPDATE form_sections SET related_model = 'CorporateAttachment' WHERE name = 'Attachments' AND module_id = 33;
UPDATE form_sections SET related_model = 'CorporateService' WHERE name = 'Services' AND module_id = 33;
