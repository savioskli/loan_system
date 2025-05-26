BEGIN;

-- Get the field_id for subcounties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTIES');

-- Get county IDs for Eastern region
SET @marsabit_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'MARSABIT');
SET @isiolo_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'ISIOLO');
SET @meru_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'MERU');
SET @tharaka_nithi_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'THARAKA_NITHI');
SET @embu_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'EMBU');
SET @kitui_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KITUI');
SET @machakos_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'MACHAKOS');
SET @makueni_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'MAKUENI');

-- Insert Marsabit subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MOYALE', 'Moyale', @marsabit_id, 1),
(@field_id, 'NORTH_HORR', 'North Horr', @marsabit_id, 1),
(@field_id, 'SAKU', 'Saku', @marsabit_id, 1),
(@field_id, 'LAISAMIS', 'Laisamis', @marsabit_id, 1);

-- Insert Isiolo subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'ISIOLO_NORTH', 'Isiolo North', @isiolo_id, 1),
(@field_id, 'ISIOLO_SOUTH', 'Isiolo South', @isiolo_id, 1);

-- Insert Meru subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'IGEMBE_SOUTH', 'Igembe South', @meru_id, 1),
(@field_id, 'IGEMBE_CENTRAL', 'Igembe Central', @meru_id, 1),
(@field_id, 'IGEMBE_NORTH', 'Igembe North', @meru_id, 1),
(@field_id, 'TIGANIA_WEST', 'Tigania West', @meru_id, 1),
(@field_id, 'TIGANIA_EAST', 'Tigania East', @meru_id, 1),
(@field_id, 'NORTH_IMENTI', 'North Imenti', @meru_id, 1),
(@field_id, 'BUURI', 'Buuri', @meru_id, 1),
(@field_id, 'CENTRAL_IMENTI', 'Central Imenti', @meru_id, 1),
(@field_id, 'SOUTH_IMENTI', 'South Imenti', @meru_id, 1);

-- Insert Tharaka-Nithi subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MAARA', 'Maara', @tharaka_nithi_id, 1),
(@field_id, 'CHUKA', 'Chuka', @tharaka_nithi_id, 1),
(@field_id, 'THARAKA', 'Tharaka', @tharaka_nithi_id, 1);

-- Insert Embu subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MANYATTA', 'Manyatta', @embu_id, 1),
(@field_id, 'RUNYENJES', 'Runyenjes', @embu_id, 1),
(@field_id, 'MBEERE_SOUTH', 'Mbeere South', @embu_id, 1),
(@field_id, 'MBEERE_NORTH', 'Mbeere North', @embu_id, 1);

-- Insert Kitui subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MWINGI_NORTH', 'Mwingi North', @kitui_id, 1),
(@field_id, 'MWINGI_WEST', 'Mwingi West', @kitui_id, 1),
(@field_id, 'MWINGI_CENTRAL', 'Mwingi Central', @kitui_id, 1),
(@field_id, 'KITUI_WEST', 'Kitui West', @kitui_id, 1),
(@field_id, 'KITUI_RURAL', 'Kitui Rural', @kitui_id, 1),
(@field_id, 'KITUI_CENTRAL', 'Kitui Central', @kitui_id, 1),
(@field_id, 'KITUI_EAST', 'Kitui East', @kitui_id, 1),
(@field_id, 'KITUI_SOUTH', 'Kitui South', @kitui_id, 1);

-- Insert Machakos subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MASINGA', 'Masinga', @machakos_id, 1),
(@field_id, 'YATTA', 'Yatta', @machakos_id, 1),
(@field_id, 'KANGUNDO', 'Kangundo', @machakos_id, 1),
(@field_id, 'MATUNGULU', 'Matungulu', @machakos_id, 1),
(@field_id, 'KATHIANI', 'Kathiani', @machakos_id, 1),
(@field_id, 'MAVOKO', 'Mavoko', @machakos_id, 1),
(@field_id, 'MACHAKOS_TOWN', 'Machakos Town', @machakos_id, 1),
(@field_id, 'MWALA', 'Mwala', @machakos_id, 1);

-- Insert Makueni subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'MBOONI', 'Mbooni', @makueni_id, 1),
(@field_id, 'KILOME', 'Kilome', @makueni_id, 1),
(@field_id, 'KAITI', 'Kaiti', @makueni_id, 1),
(@field_id, 'MAKUENI', 'Makueni', @makueni_id, 1),
(@field_id, 'KIBWEZI_WEST', 'Kibwezi West', @makueni_id, 1),
(@field_id, 'KIBWEZI_EAST', 'Kibwezi East', @makueni_id, 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
