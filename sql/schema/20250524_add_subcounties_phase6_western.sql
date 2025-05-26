BEGIN;

-- Get the field_id for subcounties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTIES');

-- Get county IDs for Western region
SET @kakamega_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KAKAMEGA');
SET @vihiga_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'VIHIGA');
SET @bungoma_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'BUNGOMA');
SET @busia_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'BUSIA');

-- Insert Kakamega subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'LUGARI', 'Lugari', @kakamega_id, 1),
(@field_id, 'LIKUYANI', 'Likuyani', @kakamega_id, 1),
(@field_id, 'MALAVA', 'Malava', @kakamega_id, 1),
(@field_id, 'LURAMBI', 'Lurambi', @kakamega_id, 1),
(@field_id, 'NAVAKHOLO', 'Navakholo', @kakamega_id, 1),
(@field_id, 'MUMIAS_WEST', 'Mumias West', @kakamega_id, 1),
(@field_id, 'MUMIAS_EAST', 'Mumias East', @kakamega_id, 1),
(@field_id, 'MATUNGU', 'Matungu', @kakamega_id, 1),
(@field_id, 'BUTERE', 'Butere', @kakamega_id, 1),
(@field_id, 'KHWISERO', 'Khwisero', @kakamega_id, 1),
(@field_id, 'SHINYALU', 'Shinyalu', @kakamega_id, 1),
(@field_id, 'IKOLOMANI', 'Ikolomani', @kakamega_id, 1);

-- Insert Vihiga subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'VIHIGA', 'Vihiga', @vihiga_id, 1),
(@field_id, 'SABATIA', 'Sabatia', @vihiga_id, 1),
(@field_id, 'HAMISI', 'Hamisi', @vihiga_id, 1),
(@field_id, 'LUANDA', 'Luanda', @vihiga_id, 1),
(@field_id, 'EMUHAYA', 'Emuhaya', @vihiga_id, 1);

-- Insert Bungoma subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MT_ELGON', 'Mt Elgon', @bungoma_id, 1),
(@field_id, 'SIRISIA', 'Sirisia', @bungoma_id, 1),
(@field_id, 'KABUCHAI', 'Kabuchai', @bungoma_id, 1),
(@field_id, 'BUMULA', 'Bumula', @bungoma_id, 1),
(@field_id, 'KANDUYI', 'Kanduyi', @bungoma_id, 1),
(@field_id, 'WEBUYE_EAST', 'Webuye East', @bungoma_id, 1),
(@field_id, 'WEBUYE_WEST', 'Webuye West', @bungoma_id, 1),
(@field_id, 'KIMILILI', 'Kimilili', @bungoma_id, 1),
(@field_id, 'TONGAREN', 'Tongaren', @bungoma_id, 1);

-- Insert Busia subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'TESO_NORTH', 'Teso North', @busia_id, 1),
(@field_id, 'TESO_SOUTH', 'Teso South', @busia_id, 1),
(@field_id, 'NAMBALE', 'Nambale', @busia_id, 1),
(@field_id, 'MATAYOS', 'Matayos', @busia_id, 1),
(@field_id, 'BUTULA', 'Butula', @busia_id, 1),
(@field_id, 'SAMIA', 'Samia', @busia_id, 1),
(@field_id, 'BUNYALA', 'Bunyala', @busia_id, 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
