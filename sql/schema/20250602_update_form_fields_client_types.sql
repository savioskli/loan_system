BEGIN;

-- Update client type restrictions for form fields
-- Example: Some fields are only visible for individual clients
UPDATE form_fields 
SET client_type_restrictions = '["individual"]'
WHERE field_name IN ('national_id', 'date_of_birth', 'marital_status');

-- Example: Some fields are only visible for corporate clients
UPDATE form_fields 
SET client_type_restrictions = '["corporate"]'
WHERE field_name IN ('registration_number', 'tax_id', 'business_type');

-- Example: Some fields are only visible for group clients
UPDATE form_fields 
SET client_type_restrictions = '["group"]'
WHERE field_name IN ('group_name', 'member_count', 'registration_certificate');

-- Example: Some fields are visible for both individual and corporate
UPDATE form_fields 
SET client_type_restrictions = '["individual", "corporate"]'
WHERE field_name IN ('phone_number', 'email', 'address');

COMMIT;
