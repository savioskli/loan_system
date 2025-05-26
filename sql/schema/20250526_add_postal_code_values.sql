-- Add Kenyan postal codes as reference values
BEGIN;

-- Nairobi Region
INSERT INTO system_reference_values (field_id, value, label, is_active, parent_value_id) VALUES
(5, '00100', 'General Post Office - Nairobi', 1, 52),
(5, '00200', 'City Square - Nairobi', 1, 52),
(5, '00300', 'Ronald Ngala Street - Nairobi', 1, 52),
(5, '00400', 'Tom Mboya Street - Nairobi', 1, 52),
(5, '00500', 'Athi River', 1, 21),  -- Machakos
(5, '00502', 'Karen - Nairobi', 1, 52),
(5, '00503', 'Kangemi - Nairobi', 1, 52),
(5, '00504', 'Kawangware - Nairobi', 1, 52),
(5, '00505', 'Langata - Nairobi', 1, 52),
(5, '00506', 'Nairobi West - Nairobi', 1, 52),
(5, '00507', 'Ruaraka - Nairobi', 1, 52),
(5, '00508', 'Buruburu - Nairobi', 1, 52),
(5, '00509', 'Parklands - Nairobi', 1, 52),
(5, '00510', 'Eastleigh - Nairobi', 1, 52),
(5, '00511', 'Embakasi - Nairobi', 1, 52),
(5, '00512', 'Industrial Area - Nairobi', 1, 52),
(5, '00513', 'Kasarani - Nairobi', 1, 52),
(5, '00514', 'Kenyatta National Hospital - Nairobi', 1, 52),
(5, '00515', 'Westlands - Nairobi', 1, 52),

-- Central Region
(5, '10100', 'Nyeri', 1, 24),  -- Nyeri
(5, '10101', 'Karatina - Nyeri', 1, 24),
(5, '10200', 'Kerugoya - Kirinyaga', 1, 25),
(5, '10300', 'Nanyuki - Laikipia', 1, 36),
(5, '10400', 'Murang\'a', 1, 26),  -- Muranga
(5, '10500', 'Thika - Kiambu', 1, 27),
(5, '10600', 'Maragua - Murang\'a', 1, 26),
(5, '10700', 'Ol Kalou - Nyandarua', 1, 23),

-- Coast Region
(5, '80100', 'Mombasa', 1, 6),  -- Mombasa
(5, '80200', 'Malindi - Kilifi', 1, 8),
(5, '80300', 'Voi - Taita Taveta', 1, 11),
(5, '80400', 'Ukunda - Kwale', 1, 7),
(5, '80500', 'Lamu', 1, 10),  -- Lamu

-- Eastern Region
(5, '60100', 'Embu', 1, 19),  -- Embu
(5, '60200', 'Meru', 1, 17),  -- Meru
(5, '60300', 'Isiolo', 1, 16),  -- Isiolo
(5, '60400', 'Kitui', 1, 20),  -- Kitui
(5, '60500', 'Marsabit', 1, 15),  -- Marsabit
(5, '60600', 'Makindu - Makueni', 1, 22),
(5, '60700', 'Garissa', 1, 12),  -- Garissa

-- Rift Valley Region
(5, '20100', 'Nakuru', 1, 37),  -- Nakuru
(5, '20200', 'Naivasha - Nakuru', 1, 37),
(5, '20300', 'Eldoret - Uasin Gishu', 1, 32),
(5, '20400', 'Kericho', 1, 40),  -- Kericho
(5, '20500', 'Kabarnet - Baringo', 1, 35),
(5, '20600', 'Kapsabet - Nandi', 1, 34),
(5, '20700', 'Nanyuki - Laikipia', 1, 36),
(5, '20800', 'Kapenguria - West Pokot', 1, 29),

-- Western Region
(5, '50100', 'Kakamega', 1, 42),  -- Kakamega
(5, '50200', 'Bungoma', 1, 44),  -- Bungoma
(5, '50300', 'Busia', 1, 45),  -- Busia
(5, '50400', 'Mumias - Kakamega', 1, 42),
(5, '50500', 'Webuye - Bungoma', 1, 44),

-- Nyanza Region
(5, '40100', 'Kisumu', 1, 47),  -- Kisumu
(5, '40200', 'Homa Bay', 1, 48),  -- Homa Bay
(5, '40300', 'Migori', 1, 49),  -- Migori
(5, '40400', 'Kisii', 1, 50),  -- Kisii
(5, '40500', 'Siaya', 1, 46),  -- Siaya
(5, '40600', 'Oyugis - Homa Bay', 1, 48),
(5, '40700', 'Rongo - Migori', 1, 49);

COMMIT;
