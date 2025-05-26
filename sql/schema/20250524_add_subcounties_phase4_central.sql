BEGIN;

-- Get the field_id for subcounties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTIES');

-- Get county IDs for Central region
SET @nyandarua_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'NYANDARUA');
SET @nyeri_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'NYERI');
SET @kirinyaga_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KIRINYAGA');
SET @muranga_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'MURANGA');
SET @kiambu_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KIAMBU');

-- Insert Nyandarua subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'KINANGOP', 'Kinangop', @nyandarua_id, 1),
(@field_id, 'KIPIPIRI', 'Kipipiri', @nyandarua_id, 1),
(@field_id, 'OL_KALOU', 'Ol Kalou', @nyandarua_id, 1),
(@field_id, 'OL_JOROK', 'Ol Jorok', @nyandarua_id, 1),
(@field_id, 'NDARAGWA', 'Ndaragwa', @nyandarua_id, 1);

-- Insert Nyeri subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'TETU', 'Tetu', @nyeri_id, 1),
(@field_id, 'KIENI_EAST', 'Kieni East', @nyeri_id, 1),
(@field_id, 'KIENI_WEST', 'Kieni West', @nyeri_id, 1),
(@field_id, 'MATHIRA_EAST', 'Mathira East', @nyeri_id, 1),
(@field_id, 'MATHIRA_WEST', 'Mathira West', @nyeri_id, 1),
(@field_id, 'NYERI_SOUTH', 'Nyeri South', @nyeri_id, 1),
(@field_id, 'MUKURWEINI', 'Mukurweini', @nyeri_id, 1),
(@field_id, 'NYERI_CENTRAL', 'Nyeri Central', @nyeri_id, 1);

-- Insert Kirinyaga subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MWEA', 'Mwea', @kirinyaga_id, 1),
(@field_id, 'GICHUGU', 'Gichugu', @kirinyaga_id, 1),
(@field_id, 'NDIA', 'Ndia', @kirinyaga_id, 1),
(@field_id, 'KIRINYAGA_CENTRAL', 'Kirinyaga Central', @kirinyaga_id, 1);

-- Insert Murang'a subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'KANGEMA', 'Kangema', @muranga_id, 1),
(@field_id, 'MATHIOYA', 'Mathioya', @muranga_id, 1),
(@field_id, 'KIHARU', 'Kiharu', @muranga_id, 1),
(@field_id, 'KIGUMO', 'Kigumo', @muranga_id, 1),
(@field_id, 'MARAGUA', 'Maragua', @muranga_id, 1),
(@field_id, 'KANDARA', 'Kandara', @muranga_id, 1),
(@field_id, 'GATANGA', 'Gatanga', @muranga_id, 1);

-- Insert Kiambu subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'GATUNDU_SOUTH', 'Gatundu South', @kiambu_id, 1),
(@field_id, 'GATUNDU_NORTH', 'Gatundu North', @kiambu_id, 1),
(@field_id, 'JUJA', 'Juja', @kiambu_id, 1),
(@field_id, 'THIKA_TOWN', 'Thika Town', @kiambu_id, 1),
(@field_id, 'RUIRU', 'Ruiru', @kiambu_id, 1),
(@field_id, 'GITHUNGURI', 'Githunguri', @kiambu_id, 1),
(@field_id, 'KIAMBU', 'Kiambu', @kiambu_id, 1),
(@field_id, 'KIAMBAA', 'Kiambaa', @kiambu_id, 1),
(@field_id, 'KABETE', 'Kabete', @kiambu_id, 1),
(@field_id, 'KIKUYU', 'Kikuyu', @kiambu_id, 1),
(@field_id, 'LIMURU', 'Limuru', @kiambu_id, 1),
(@field_id, 'LARI', 'Lari', @kiambu_id, 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
