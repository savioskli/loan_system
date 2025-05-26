BEGIN;

-- First, create the subcounties reference field if it doesn't exist
INSERT INTO system_reference_fields (code, name, description, is_active)
SELECT 'SUBCOUNTIES', 'Sub Counties', 'List of sub counties in Kenya', 1
WHERE NOT EXISTS (
    SELECT 1 FROM system_reference_fields WHERE code = 'SUBCOUNTIES'
);

-- Get the field_id for subcounties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTIES');

-- Get county IDs
SET @mombasa_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'MOMBASA');
SET @nairobi_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'NAIROBI');
SET @kisumu_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KISUMU');
SET @nakuru_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'NAKURU');

-- Insert Mombasa subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MVITA', 'Mvita', @mombasa_id, 1),
(@field_id, 'NYALI', 'Nyali', @mombasa_id, 1),
(@field_id, 'KISAUNI', 'Kisauni', @mombasa_id, 1),
(@field_id, 'CHANGAMWE', 'Changamwe', @mombasa_id, 1),
(@field_id, 'JOMVU', 'Jomvu', @mombasa_id, 1),
(@field_id, 'LIKONI', 'Likoni', @mombasa_id, 1);

-- Insert Nairobi subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'WESTLANDS', 'Westlands', @nairobi_id, 1),
(@field_id, 'DAGORETTI_NORTH', 'Dagoretti North', @nairobi_id, 1),
(@field_id, 'DAGORETTI_SOUTH', 'Dagoretti South', @nairobi_id, 1),
(@field_id, 'LANGATA', 'Langata', @nairobi_id, 1),
(@field_id, 'KIBRA', 'Kibra', @nairobi_id, 1),
(@field_id, 'ROYSAMBU', 'Roysambu', @nairobi_id, 1),
(@field_id, 'KASARANI', 'Kasarani', @nairobi_id, 1),
(@field_id, 'RUARAKA', 'Ruaraka', @nairobi_id, 1),
(@field_id, 'EMBAKASI_SOUTH', 'Embakasi South', @nairobi_id, 1),
(@field_id, 'EMBAKASI_NORTH', 'Embakasi North', @nairobi_id, 1),
(@field_id, 'EMBAKASI_CENTRAL', 'Embakasi Central', @nairobi_id, 1),
(@field_id, 'EMBAKASI_EAST', 'Embakasi East', @nairobi_id, 1),
(@field_id, 'EMBAKASI_WEST', 'Embakasi West', @nairobi_id, 1),
(@field_id, 'MAKADARA', 'Makadara', @nairobi_id, 1),
(@field_id, 'KAMUKUNJI', 'Kamukunji', @nairobi_id, 1),
(@field_id, 'STAREHE', 'Starehe', @nairobi_id, 1),
(@field_id, 'MATHARE', 'Mathare', @nairobi_id, 1);

-- Insert Kisumu subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'KISUMU_CENTRAL', 'Kisumu Central', @kisumu_id, 1),
(@field_id, 'KISUMU_EAST', 'Kisumu East', @kisumu_id, 1),
(@field_id, 'KISUMU_WEST', 'Kisumu West', @kisumu_id, 1),
(@field_id, 'SEME', 'Seme', @kisumu_id, 1),
(@field_id, 'NYANDO', 'Nyando', @kisumu_id, 1),
(@field_id, 'MUHORONI', 'Muhoroni', @kisumu_id, 1),
(@field_id, 'NYAKACH', 'Nyakach', @kisumu_id, 1);

-- Insert Nakuru subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'NAKURU_TOWN_EAST', 'Nakuru Town East', @nakuru_id, 1),
(@field_id, 'NAKURU_TOWN_WEST', 'Nakuru Town West', @nakuru_id, 1),
(@field_id, 'NAIVASHA', 'Naivasha', @nakuru_id, 1),
(@field_id, 'GILGIL', 'Gilgil', @nakuru_id, 1),
(@field_id, 'KURESOI_SOUTH', 'Kuresoi South', @nakuru_id, 1),
(@field_id, 'KURESOI_NORTH', 'Kuresoi North', @nakuru_id, 1),
(@field_id, 'MOLO', 'Molo', @nakuru_id, 1),
(@field_id, 'RONGAI', 'Rongai', @nakuru_id, 1),
(@field_id, 'SUBUKIA', 'Subukia', @nakuru_id, 1),
(@field_id, 'BAHATI', 'Bahati', @nakuru_id, 1),
(@field_id, 'NJORO', 'Njoro', @nakuru_id, 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
