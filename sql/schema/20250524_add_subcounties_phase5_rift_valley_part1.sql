BEGIN;

-- Get the field_id for subcounties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTIES');

-- Get county IDs for Rift Valley region (Part 1)
SET @turkana_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'TURKANA');
SET @west_pokot_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'WEST_POKOT');
SET @samburu_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'SAMBURU');
SET @trans_nzoia_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'TRANS_NZOIA');
SET @uasin_gishu_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'UASIN_GISHU');
SET @elgeyo_marakwet_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'ELGEYO_MARAKWET');

-- Insert Turkana subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'TURKANA_NORTH', 'Turkana North', @turkana_id, 1),
(@field_id, 'TURKANA_WEST', 'Turkana West', @turkana_id, 1),
(@field_id, 'TURKANA_CENTRAL', 'Turkana Central', @turkana_id, 1),
(@field_id, 'LOIMA', 'Loima', @turkana_id, 1),
(@field_id, 'TURKANA_SOUTH', 'Turkana South', @turkana_id, 1),
(@field_id, 'TURKANA_EAST', 'Turkana East', @turkana_id, 1);

-- Insert West Pokot subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'KAPENGURIA', 'Kapenguria', @west_pokot_id, 1),
(@field_id, 'SIGOR', 'Sigor', @west_pokot_id, 1),
(@field_id, 'KACHELIBA', 'Kacheliba', @west_pokot_id, 1),
(@field_id, 'POKOT_SOUTH', 'Pokot South', @west_pokot_id, 1);

-- Insert Samburu subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'SAMBURU_WEST', 'Samburu West', @samburu_id, 1),
(@field_id, 'SAMBURU_NORTH', 'Samburu North', @samburu_id, 1),
(@field_id, 'SAMBURU_EAST', 'Samburu East', @samburu_id, 1);

-- Insert Trans Nzoia subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'KWANZA', 'Kwanza', @trans_nzoia_id, 1),
(@field_id, 'ENDEBESS', 'Endebess', @trans_nzoia_id, 1),
(@field_id, 'SABOTI', 'Saboti', @trans_nzoia_id, 1),
(@field_id, 'KIMININI', 'Kiminini', @trans_nzoia_id, 1),
(@field_id, 'CHERANGANY', 'Cherangany', @trans_nzoia_id, 1);

-- Insert Uasin Gishu subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'SOY', 'Soy', @uasin_gishu_id, 1),
(@field_id, 'TURBO', 'Turbo', @uasin_gishu_id, 1),
(@field_id, 'MOIBEN', 'Moiben', @uasin_gishu_id, 1),
(@field_id, 'AINABKOI', 'Ainabkoi', @uasin_gishu_id, 1),
(@field_id, 'KAPSERET', 'Kapseret', @uasin_gishu_id, 1),
(@field_id, 'KESSES', 'Kesses', @uasin_gishu_id, 1);

-- Insert Elgeyo Marakwet subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MARAKWET_EAST', 'Marakwet East', @elgeyo_marakwet_id, 1),
(@field_id, 'MARAKWET_WEST', 'Marakwet West', @elgeyo_marakwet_id, 1),
(@field_id, 'KEIYO_NORTH', 'Keiyo North', @elgeyo_marakwet_id, 1),
(@field_id, 'KEIYO_SOUTH', 'Keiyo South', @elgeyo_marakwet_id, 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
