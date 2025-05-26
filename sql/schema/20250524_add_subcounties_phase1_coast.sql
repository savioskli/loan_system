BEGIN;

-- Get the field_id for subcounties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTIES');

-- Get county IDs for Coast region
SET @kwale_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KWALE');
SET @kilifi_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KILIFI');
SET @tana_river_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'TANA_RIVER');
SET @lamu_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'LAMU');
SET @taita_taveta_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'TAITA_TAVETA');

-- Insert Kwale subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MATUGA', 'Matuga', @kwale_id, 1),
(@field_id, 'MSAMBWENI', 'Msambweni', @kwale_id, 1),
(@field_id, 'LUNGA_LUNGA', 'Lunga Lunga', @kwale_id, 1),
(@field_id, 'KINANGO', 'Kinango', @kwale_id, 1);

-- Insert Kilifi subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'KILIFI_NORTH', 'Kilifi North', @kilifi_id, 1),
(@field_id, 'KILIFI_SOUTH', 'Kilifi South', @kilifi_id, 1),
(@field_id, 'GANZE', 'Ganze', @kilifi_id, 1),
(@field_id, 'MALINDI', 'Malindi', @kilifi_id, 1),
(@field_id, 'MAGARINI', 'Magarini', @kilifi_id, 1),
(@field_id, 'RABAI', 'Rabai', @kilifi_id, 1),
(@field_id, 'KALOLENI', 'Kaloleni', @kilifi_id, 1);

-- Insert Tana River subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'GARSEN', 'Garsen', @tana_river_id, 1),
(@field_id, 'GALOLE', 'Galole', @tana_river_id, 1),
(@field_id, 'BURA', 'Bura', @tana_river_id, 1);

-- Insert Lamu subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'LAMU_EAST', 'Lamu East', @lamu_id, 1),
(@field_id, 'LAMU_WEST', 'Lamu West', @lamu_id, 1);

-- Insert Taita Taveta subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'TAVETA', 'Taveta', @taita_taveta_id, 1),
(@field_id, 'WUNDANYI', 'Wundanyi', @taita_taveta_id, 1),
(@field_id, 'MWATATE', 'Mwatate', @taita_taveta_id, 1),
(@field_id, 'VOI', 'Voi', @taita_taveta_id, 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
