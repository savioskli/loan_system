BEGIN;

-- Add client type field to General Information section
INSERT INTO form_fields (
    module_id,
    organization_id,
    field_name,
    field_label,
    field_type,
    is_required,
    field_order,
    section_id,
    is_system,
    system_reference_field_id,
    is_visible,
    created_at,
    updated_at
) VALUES (
    32, -- Prospect Registration module
    1,  -- Default organization
    'client_type',
    'Client Type',
    'select',
    true,
    1,   -- First field in the section
    18,  -- General Information section
    true,
    1,   -- Client type reference field ID
    true,
    NOW(),
    NOW()
);

COMMIT;
