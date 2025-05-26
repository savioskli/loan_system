BEGIN;

-- Get the field_id for subcounties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTIES');

-- Get county IDs for Nyanza region
SET @siaya_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'SIAYA');
SET @homa_bay_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'HOMA_BAY');
SET @migori_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'MIGORI');
SET @kisii_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KISII');
SET @nyamira_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'NYAMIRA');

-- Insert Siaya subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'ALEGO_USONGA', 'Alego Usonga', @siaya_id, 1),
(@field_id, 'GEM', 'Gem', @siaya_id, 1),
(@field_id, 'BONDO', 'Bondo', @siaya_id, 1),
(@field_id, 'RARIEDA', 'Rarieda', @siaya_id, 1),
(@field_id, 'UGENYA', 'Ugenya', @siaya_id, 1),
(@field_id, 'UGUNJA', 'Ugunja', @siaya_id, 1);

-- Insert Homa Bay subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'KASIPUL', 'Kasipul', @homa_bay_id, 1),
(@field_id, 'KABONDO_KASIPUL', 'Kabondo Kasipul', @homa_bay_id, 1),
(@field_id, 'KARACHUONYO', 'Karachuonyo', @homa_bay_id, 1),
(@field_id, 'RANGWE', 'Rangwe', @homa_bay_id, 1),
(@field_id, 'HOMA_BAY_TOWN', 'Homa Bay Town', @homa_bay_id, 1),
(@field_id, 'NDHIWA', 'Ndhiwa', @homa_bay_id, 1),
(@field_id, 'MBITA', 'Mbita', @homa_bay_id, 1),
(@field_id, 'SUBA', 'Suba', @homa_bay_id, 1);

-- Insert Migori subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'RONGO', 'Rongo', @migori_id, 1),
(@field_id, 'AWENDO', 'Awendo', @migori_id, 1),
(@field_id, 'SUNA_EAST', 'Suna East', @migori_id, 1),
(@field_id, 'SUNA_WEST', 'Suna West', @migori_id, 1),
(@field_id, 'URIRI', 'Uriri', @migori_id, 1),
(@field_id, 'NYATIKE', 'Nyatike', @migori_id, 1),
(@field_id, 'KURIA_WEST', 'Kuria West', @migori_id, 1),
(@field_id, 'KURIA_EAST', 'Kuria East', @migori_id, 1);

-- Insert Kisii subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'BONCHARI', 'Bonchari', @kisii_id, 1),
(@field_id, 'SOUTH_MUGIRANGO', 'South Mugirango', @kisii_id, 1),
(@field_id, 'BOMACHOGE_BORABU', 'Bomachoge Borabu', @kisii_id, 1),
(@field_id, 'BOBASI', 'Bobasi', @kisii_id, 1),
(@field_id, 'BOMACHOGE_CHACHE', 'Bomachoge Chache', @kisii_id, 1),
(@field_id, 'NYARIBARI_MASABA', 'Nyaribari Masaba', @kisii_id, 1),
(@field_id, 'NYARIBARI_CHACHE', 'Nyaribari Chache', @kisii_id, 1),
(@field_id, 'KITUTU_CHACHE_NORTH', 'Kitutu Chache North', @kisii_id, 1),
(@field_id, 'KITUTU_CHACHE_SOUTH', 'Kitutu Chache South', @kisii_id, 1);

-- Insert Nyamira subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'KITUTU_MASABA', 'Kitutu Masaba', @nyamira_id, 1),
(@field_id, 'WEST_MUGIRANGO', 'West Mugirango', @nyamira_id, 1),
(@field_id, 'NORTH_MUGIRANGO', 'North Mugirango', @nyamira_id, 1),
(@field_id, 'BORABU', 'Borabu', @nyamira_id, 1),
(@field_id, 'MANGA', 'Manga', @nyamira_id, 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
