BEGIN;

-- Get the field_id for subcounties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTIES');

-- Get county IDs for North Eastern region
SET @garissa_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'GARISSA');
SET @wajir_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'WAJIR');
SET @mandera_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'MANDERA');

-- Insert Garissa subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'GARISSA_TOWNSHIP', 'Garissa Township', @garissa_id, 1),
(@field_id, 'BALAMBALA', 'Balambala', @garissa_id, 1),
(@field_id, 'LAGDERA', 'Lagdera', @garissa_id, 1),
(@field_id, 'DADAAB', 'Dadaab', @garissa_id, 1),
(@field_id, 'FAFI', 'Fafi', @garissa_id, 1),
(@field_id, 'IJARA', 'Ijara', @garissa_id, 1);

-- Insert Wajir subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'WAJIR_NORTH', 'Wajir North', @wajir_id, 1),
(@field_id, 'WAJIR_EAST', 'Wajir East', @wajir_id, 1),
(@field_id, 'TARBAJ', 'Tarbaj', @wajir_id, 1),
(@field_id, 'WAJIR_WEST', 'Wajir West', @wajir_id, 1),
(@field_id, 'ELDAS', 'Eldas', @wajir_id, 1),
(@field_id, 'WAJIR_SOUTH', 'Wajir South', @wajir_id, 1);

-- Insert Mandera subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MANDERA_WEST', 'Mandera West', @mandera_id, 1),
(@field_id, 'BANISSA', 'Banissa', @mandera_id, 1),
(@field_id, 'MANDERA_NORTH', 'Mandera North', @mandera_id, 1),
(@field_id, 'MANDERA_SOUTH', 'Mandera South', @mandera_id, 1),
(@field_id, 'MANDERA_EAST', 'Mandera East', @mandera_id, 1),
(@field_id, 'LAFEY', 'Lafey', @mandera_id, 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
