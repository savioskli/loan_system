BEGIN;

-- First, create the counties reference field if it doesn't exist
INSERT INTO system_reference_fields (code, name, description, is_active)
SELECT 'COUNTIES', 'Counties', 'List of counties in Kenya', 1
WHERE NOT EXISTS (
    SELECT 1 FROM system_reference_fields WHERE code = 'COUNTIES'
);

-- Get the field_id for counties
SET @field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTIES');

-- Insert counties
INSERT INTO system_reference_values (field_id, value, label, is_active) VALUES
(@field_id, 'MOMBASA', 'Mombasa', 1),
(@field_id, 'KWALE', 'Kwale', 1),
(@field_id, 'KILIFI', 'Kilifi', 1),
(@field_id, 'TANA_RIVER', 'Tana River', 1),
(@field_id, 'LAMU', 'Lamu', 1),
(@field_id, 'TAITA_TAVETA', 'Taita Taveta', 1),
(@field_id, 'GARISSA', 'Garissa', 1),
(@field_id, 'WAJIR', 'Wajir', 1),
(@field_id, 'MANDERA', 'Mandera', 1),
(@field_id, 'MARSABIT', 'Marsabit', 1),
(@field_id, 'ISIOLO', 'Isiolo', 1),
(@field_id, 'MERU', 'Meru', 1),
(@field_id, 'THARAKA_NITHI', 'Tharaka-Nithi', 1),
(@field_id, 'EMBU', 'Embu', 1),
(@field_id, 'KITUI', 'Kitui', 1),
(@field_id, 'MACHAKOS', 'Machakos', 1),
(@field_id, 'MAKUENI', 'Makueni', 1),
(@field_id, 'NYANDARUA', 'Nyandarua', 1),
(@field_id, 'NYERI', 'Nyeri', 1),
(@field_id, 'KIRINYAGA', 'Kirinyaga', 1),
(@field_id, 'MURANGA', "Murang'a", 1),
(@field_id, 'KIAMBU', 'Kiambu', 1),
(@field_id, 'TURKANA', 'Turkana', 1),
(@field_id, 'WEST_POKOT', 'West Pokot', 1),
(@field_id, 'SAMBURU', 'Samburu', 1),
(@field_id, 'TRANS_NZOIA', 'Trans Nzoia', 1),
(@field_id, 'UASIN_GISHU', 'Uasin Gishu', 1),
(@field_id, 'ELGEYO_MARAKWET', 'Elgeyo Marakwet', 1),
(@field_id, 'NANDI', 'Nandi', 1),
(@field_id, 'BARINGO', 'Baringo', 1),
(@field_id, 'LAIKIPIA', 'Laikipia', 1),
(@field_id, 'NAKURU', 'Nakuru', 1),
(@field_id, 'NAROK', 'Narok', 1),
(@field_id, 'KAJIADO', 'Kajiado', 1),
(@field_id, 'KERICHO', 'Kericho', 1),
(@field_id, 'BOMET', 'Bomet', 1),
(@field_id, 'KAKAMEGA', 'Kakamega', 1),
(@field_id, 'VIHIGA', 'Vihiga', 1),
(@field_id, 'BUNGOMA', 'Bungoma', 1),
(@field_id, 'BUSIA', 'Busia', 1),
(@field_id, 'SIAYA', 'Siaya', 1),
(@field_id, 'KISUMU', 'Kisumu', 1),
(@field_id, 'HOMA_BAY', 'Homa Bay', 1),
(@field_id, 'MIGORI', 'Migori', 1),
(@field_id, 'KISII', 'Kisii', 1),
(@field_id, 'NYAMIRA', 'Nyamira', 1),
(@field_id, 'NAIROBI', 'Nairobi', 1);

COMMIT;

-- Rollback in case of errors
-- ROLLBACK;
