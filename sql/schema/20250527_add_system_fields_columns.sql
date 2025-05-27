BEGIN;

-- Add is_system column
ALTER TABLE form_fields ADD COLUMN is_system BOOLEAN DEFAULT FALSE;

-- Add system_reference_field_id column
ALTER TABLE form_fields ADD COLUMN system_reference_field_id INTEGER,
    ADD CONSTRAINT fk_system_reference_field
    FOREIGN KEY (system_reference_field_id)
    REFERENCES form_fields(id)
    ON DELETE SET NULL;

COMMIT;
