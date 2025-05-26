-- Add Kenyan postal codes table and data
BEGIN;

CREATE TABLE IF NOT EXISTS postal_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    location VARCHAR(100) NOT NULL,
    county VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_postal_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert Kenyan postal codes
INSERT INTO postal_codes (code, location, county) VALUES
-- Nairobi Region
('00100', 'General Post Office', 'Nairobi'),
('00200', 'City Square', 'Nairobi'),
('00300', 'Ronald Ngala Street', 'Nairobi'),
('00400', 'Tom Mboya Street', 'Nairobi'),
('00500', 'Athi River', 'Machakos'),
('00502', 'Karen', 'Nairobi'),
('00503', 'Kangemi', 'Nairobi'),
('00504', 'Kawangware', 'Nairobi'),
('00505', 'Langata', 'Nairobi'),
('00506', 'Nairobi West', 'Nairobi'),
('00507', 'Ruaraka', 'Nairobi'),
('00508', 'Buruburu', 'Nairobi'),
('00509', 'Parklands', 'Nairobi'),
('00510', 'Eastleigh', 'Nairobi'),
('00511', 'Embakasi', 'Nairobi'),
('00512', 'Industrial Area', 'Nairobi'),
('00513', 'Kasarani', 'Nairobi'),
('00514', 'Kenyatta National Hospital', 'Nairobi'),
('00515', 'Westlands', 'Nairobi'),

-- Central Region
('10100', 'Nyeri', 'Nyeri'),
('10101', 'Karatina', 'Nyeri'),
('10200', 'Kerugoya', 'Kirinyaga'),
('10300', 'Nanyuki', 'Laikipia'),
('10400', 'Murang\'a', 'Murang\'a'),
('10500', 'Thika', 'Kiambu'),
('10600', 'Maragua', 'Murang\'a'),
('10700', 'Ol Kalou', 'Nyandarua'),

-- Coast Region
('80100', 'Mombasa', 'Mombasa'),
('80200', 'Malindi', 'Kilifi'),
('80300', 'Voi', 'Taita Taveta'),
('80400', 'Ukunda', 'Kwale'),
('80500', 'Lamu', 'Lamu'),

-- Eastern Region
('60100', 'Embu', 'Embu'),
('60200', 'Meru', 'Meru'),
('60300', 'Isiolo', 'Isiolo'),
('60400', 'Kitui', 'Kitui'),
('60500', 'Marsabit', 'Marsabit'),
('60600', 'Makindu', 'Makueni'),
('60700', 'Garissa', 'Garissa'),

-- Rift Valley Region
('20100', 'Nakuru', 'Nakuru'),
('20200', 'Naivasha', 'Nakuru'),
('20300', 'Eldoret', 'Uasin Gishu'),
('20400', 'Kericho', 'Kericho'),
('20500', 'Kabarnet', 'Baringo'),
('20600', 'Kapsabet', 'Nandi'),
('20700', 'Nanyuki', 'Laikipia'),
('20800', 'Kapenguria', 'West Pokot'),

-- Western Region
('50100', 'Kakamega', 'Kakamega'),
('50200', 'Bungoma', 'Bungoma'),
('50300', 'Busia', 'Busia'),
('50400', 'Mumias', 'Kakamega'),
('50500', 'Webuye', 'Bungoma'),

-- Nyanza Region
('40100', 'Kisumu', 'Kisumu'),
('40200', 'Homa Bay', 'Homa Bay'),
('40300', 'Migori', 'Migori'),
('40400', 'Kisii', 'Kisii'),
('40500', 'Siaya', 'Siaya'),
('40600', 'Oyugis', 'Homa Bay'),
('40700', 'Rongo', 'Migori');

COMMIT;
