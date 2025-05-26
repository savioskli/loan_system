-- Add system field columns
BEGIN;

-- Add is_system and system_reference_field_id columns to form_fields table
ALTER TABLE form_fields
ADD COLUMN is_system BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN system_reference_field_id INT,
ADD CONSTRAINT fk_system_reference_field
    FOREIGN KEY (system_reference_field_id)
    REFERENCES system_reference_fields(id)
    ON DELETE SET NULL;

COMMIT;
