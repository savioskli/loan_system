-- Add branch reference field and values
BEGIN;

-- Add branch reference field
INSERT INTO system_reference_fields (code, name, description, is_active)
VALUES ('BRANCHES', 'Branches', 'Bank branches across Kenyan towns', 1);

-- Get the field ID for branches
SET @branch_field_id = LAST_INSERT_ID();

-- Add county values (as parent values)
INSERT INTO system_reference_values (field_id, value, label, is_active) VALUES
-- Major Counties
(@branch_field_id, 'NAIROBI', 'Nairobi County', 1),
(@branch_field_id, 'MOMBASA', 'Mombasa County', 1),
(@branch_field_id, 'KISUMU', 'Kisumu County', 1),
(@branch_field_id, 'NAKURU', 'Nakuru County', 1),
(@branch_field_id, 'UASIN_GISHU', 'Uasin Gishu County', 1),
(@branch_field_id, 'KIAMBU', 'Kiambu County', 1),
(@branch_field_id, 'MACHAKOS', 'Machakos County', 1),
(@branch_field_id, 'MERU', 'Meru County', 1),
(@branch_field_id, 'KAKAMEGA', 'Kakamega County', 1),
(@branch_field_id, 'KILIFI', 'Kilifi County', 1);

-- Store county IDs for reference
SET @nairobi_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'NAIROBI');
SET @mombasa_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'MOMBASA');
SET @kisumu_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'KISUMU');
SET @nakuru_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'NAKURU');
SET @uasin_gishu_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'UASIN_GISHU');
SET @kiambu_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'KIAMBU');
SET @machakos_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'MACHAKOS');
SET @meru_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'MERU');
SET @kakamega_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'KAKAMEGA');
SET @kilifi_id = (SELECT id FROM system_reference_values WHERE field_id = @branch_field_id AND value = 'KILIFI');

-- Add branch values with their respective county parents
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
-- Nairobi County Branches
(@branch_field_id, 'NAIROBI_CBD', 'Nairobi CBD', @nairobi_id, 1),
(@branch_field_id, 'WESTLANDS', 'Westlands', @nairobi_id, 1),
(@branch_field_id, 'EASTLEIGH', 'Eastleigh', @nairobi_id, 1),
(@branch_field_id, 'KAREN', 'Karen', @nairobi_id, 1),
(@branch_field_id, 'KASARANI', 'Kasarani', @nairobi_id, 1),

-- Mombasa County Branches
(@branch_field_id, 'MOMBASA_CBD', 'Mombasa CBD', @mombasa_id, 1),
(@branch_field_id, 'NYALI', 'Nyali', @mombasa_id, 1),
(@branch_field_id, 'BAMBURI', 'Bamburi', @mombasa_id, 1),
(@branch_field_id, 'LIKONI', 'Likoni', @mombasa_id, 1),

-- Kisumu County Branches
(@branch_field_id, 'KISUMU_CBD', 'Kisumu CBD', @kisumu_id, 1),
(@branch_field_id, 'KONDELE', 'Kondele', @kisumu_id, 1),
(@branch_field_id, 'KISUMU_WEST', 'Kisumu West', @kisumu_id, 1),

-- Nakuru County Branches
(@branch_field_id, 'NAKURU_CBD', 'Nakuru CBD', @nakuru_id, 1),
(@branch_field_id, 'NAIVASHA', 'Naivasha', @nakuru_id, 1),
(@branch_field_id, 'GILGIL', 'Gilgil', @nakuru_id, 1),

-- Uasin Gishu County Branches
(@branch_field_id, 'ELDORET_CBD', 'Eldoret CBD', @uasin_gishu_id, 1),
(@branch_field_id, 'ELDORET_WEST', 'Eldoret West', @uasin_gishu_id, 1),
(@branch_field_id, 'BURNT_FOREST', 'Burnt Forest', @uasin_gishu_id, 1),

-- Kiambu County Branches
(@branch_field_id, 'THIKA', 'Thika', @kiambu_id, 1),
(@branch_field_id, 'RUIRU', 'Ruiru', @kiambu_id, 1),
(@branch_field_id, 'KIAMBU_TOWN', 'Kiambu Town', @kiambu_id, 1),
(@branch_field_id, 'LIMURU', 'Limuru', @kiambu_id, 1),

-- Machakos County Branches
(@branch_field_id, 'MACHAKOS_TOWN', 'Machakos Town', @machakos_id, 1),
(@branch_field_id, 'ATHI_RIVER', 'Athi River', @machakos_id, 1),
(@branch_field_id, 'MAVOKO', 'Mavoko', @machakos_id, 1),

-- Meru County Branches
(@branch_field_id, 'MERU_TOWN', 'Meru Town', @meru_id, 1),
(@branch_field_id, 'NKUBU', 'Nkubu', @meru_id, 1),
(@branch_field_id, 'MAUA', 'Maua', @meru_id, 1),

-- Kakamega County Branches
(@branch_field_id, 'KAKAMEGA_CBD', 'Kakamega CBD', @kakamega_id, 1),
(@branch_field_id, 'MUMIAS', 'Mumias', @kakamega_id, 1),
(@branch_field_id, 'BUTERE', 'Butere', @kakamega_id, 1),

-- Kilifi County Branches
(@branch_field_id, 'KILIFI_TOWN', 'Kilifi Town', @kilifi_id, 1),
(@branch_field_id, 'MALINDI', 'Malindi', @kilifi_id, 1),
(@branch_field_id, 'WATAMU', 'Watamu', @kilifi_id, 1);

COMMIT;
