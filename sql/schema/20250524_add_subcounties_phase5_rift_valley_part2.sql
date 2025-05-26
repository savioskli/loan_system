BEGIN;

-- Get the field_id for subcounties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTIES');

-- Get county IDs for Rift Valley region (Part 2)
SET @nandi_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'NANDI');
SET @baringo_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'BARINGO');
SET @laikipia_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'LAIKIPIA');
SET @narok_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'NAROK');
SET @kajiado_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KAJIADO');
SET @kericho_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'KERICHO');
SET @bomet_id = (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES') AND value = 'BOMET');

-- Insert Nandi subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'CHESUMEI', 'Chesumei', @nandi_id, 1),
(@field_id, 'NANDI_EAST', 'Nandi East', @nandi_id, 1),
(@field_id, 'NANDI_SOUTH', 'Nandi South', @nandi_id, 1),
(@field_id, 'NANDI_CENTRAL', 'Nandi Central', @nandi_id, 1),
(@field_id, 'NANDI_NORTH', 'Nandi North', @nandi_id, 1),
(@field_id, 'TINDERET', 'Tinderet', @nandi_id, 1);

-- Insert Baringo subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'TIATY', 'Tiaty', @baringo_id, 1),
(@field_id, 'BARINGO_NORTH', 'Baringo North', @baringo_id, 1),
(@field_id, 'BARINGO_CENTRAL', 'Baringo Central', @baringo_id, 1),
(@field_id, 'BARINGO_SOUTH', 'Baringo South', @baringo_id, 1),
(@field_id, 'MOGOTIO', 'Mogotio', @baringo_id, 1),
(@field_id, 'ELDAMA_RAVINE', 'Eldama Ravine', @baringo_id, 1);

-- Insert Laikipia subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'LAIKIPIA_WEST', 'Laikipia West', @laikipia_id, 1),
(@field_id, 'LAIKIPIA_EAST', 'Laikipia East', @laikipia_id, 1),
(@field_id, 'LAIKIPIA_NORTH', 'Laikipia North', @laikipia_id, 1);

-- Insert Narok subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'NAROK_NORTH', 'Narok North', @narok_id, 1),
(@field_id, 'NAROK_SOUTH', 'Narok South', @narok_id, 1),
(@field_id, 'NAROK_EAST', 'Narok East', @narok_id, 1),
(@field_id, 'NAROK_WEST', 'Narok West', @narok_id, 1),
(@field_id, 'KILGORIS', 'Kilgoris', @narok_id, 1),
(@field_id, 'EMURUA_DIKIRR', 'Emurua Dikirr', @narok_id, 1);

-- Insert Kajiado subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'KAJIADO_CENTRAL', 'Kajiado Central', @kajiado_id, 1),
(@field_id, 'KAJIADO_NORTH', 'Kajiado North', @kajiado_id, 1),
(@field_id, 'KAJIADO_SOUTH', 'Kajiado South', @kajiado_id, 1),
(@field_id, 'KAJIADO_EAST', 'Kajiado East', @kajiado_id, 1),
(@field_id, 'KAJIADO_WEST', 'Kajiado West', @kajiado_id, 1);

-- Insert Kericho subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'AINAMOI', 'Ainamoi', @kericho_id, 1),
(@field_id, 'BELGUT', 'Belgut', @kericho_id, 1),
(@field_id, 'BURETI', 'Bureti', @kericho_id, 1),
(@field_id, 'KIPKELION_EAST', 'Kipkelion East', @kericho_id, 1),
(@field_id, 'KIPKELION_WEST', 'Kipkelion West', @kericho_id, 1),
(@field_id, 'SIGOWET_SOIN', 'Sigowet/Soin', @kericho_id, 1);

-- Insert Bomet subcounties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
(@field_id, 'BOMET_CENTRAL', 'Bomet Central', @bomet_id, 1),
(@field_id, 'BOMET_EAST', 'Bomet East', @bomet_id, 1),
(@field_id, 'CHEPALUNGU', 'Chepalungu', @bomet_id, 1),
(@field_id, 'SOTIK', 'Sotik', @bomet_id, 1),
(@field_id, 'KONOIN', 'Konoin', @bomet_id, 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
