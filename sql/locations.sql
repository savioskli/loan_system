-- Create counties table
CREATE TABLE IF NOT EXISTS counties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    FOREIGN KEY (created_by) REFERENCES staff(id),
    FOREIGN KEY (updated_by) REFERENCES staff(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create subcounties table
CREATE TABLE IF NOT EXISTS subcounties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    county_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    FOREIGN KEY (county_id) REFERENCES counties(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES staff(id),
    FOREIGN KEY (updated_by) REFERENCES staff(id),
    UNIQUE KEY uq_subcounty_name_county (name, county_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create wards table
CREATE TABLE IF NOT EXISTS wards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subcounty_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    FOREIGN KEY (subcounty_id) REFERENCES subcounties(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES staff(id),
    FOREIGN KEY (updated_by) REFERENCES staff(id),
    UNIQUE KEY uq_ward_name_subcounty (name, subcounty_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert counties
INSERT INTO counties (name, code) VALUES
('Mombasa', '001'),
('Kwale', '002'),
('Kilifi', '003'),
('Tana River', '004'),
('Lamu', '005'),
('Taita Taveta', '006'),
('Garissa', '007'),
('Wajir', '008'),
('Mandera', '009'),
('Marsabit', '010'),
('Isiolo', '011'),
('Meru', '012'),
('Tharaka Nithi', '013'),
('Embu', '014'),
('Kitui', '015'),
('Machakos', '016'),
('Makueni', '017'),
('Nyandarua', '018'),
('Nyeri', '019'),
('Kirinyaga', '020'),
('Murang''a', '021'),
('Kiambu', '022'),
('Turkana', '023'),
('West Pokot', '024'),
('Samburu', '025'),
('Trans Nzoia', '026'),
('Uasin Gishu', '027'),
('Elgeyo Marakwet', '028'),
('Nandi', '029'),
('Baringo', '030'),
('Laikipia', '031'),
('Nakuru', '032'),
('Narok', '033'),
('Kajiado', '034'),
('Kericho', '035'),
('Bomet', '036'),
('Kakamega', '037'),
('Vihiga', '038'),
('Bungoma', '039'),
('Busia', '040'),
('Siaya', '041'),
('Kisumu', '042'),
('Homa Bay', '043'),
('Migori', '044'),
('Kisii', '045'),
('Nyamira', '046'),
('Nairobi', '047');

-- Insert sample subcounties for Nairobi (you should add all subcounties for all counties)
INSERT INTO subcounties (name, county_id) VALUES
('Dagoretti North', (SELECT id FROM counties WHERE code = '047')),
('Dagoretti South', (SELECT id FROM counties WHERE code = '047')),
('Embakasi Central', (SELECT id FROM counties WHERE code = '047')),
('Embakasi East', (SELECT id FROM counties WHERE code = '047')),
('Embakasi North', (SELECT id FROM counties WHERE code = '047')),
('Embakasi South', (SELECT id FROM counties WHERE code = '047')),
('Embakasi West', (SELECT id FROM counties WHERE code = '047')),
('Kamukunji', (SELECT id FROM counties WHERE code = '047')),
('Kasarani', (SELECT id FROM counties WHERE code = '047')),
('Kibra', (SELECT id FROM counties WHERE code = '047')),
('Lang''ata', (SELECT id FROM counties WHERE code = '047')),
('Makadara', (SELECT id FROM counties WHERE code = '047')),
('Mathare', (SELECT id FROM counties WHERE code = '047')),
('Roysambu', (SELECT id FROM counties WHERE code = '047')),
('Ruaraka', (SELECT id FROM counties WHERE code = '047')),
('Starehe', (SELECT id FROM counties WHERE code = '047')),
('Westlands', (SELECT id FROM counties WHERE code = '047'));

-- Insert sample wards for Westlands subcounty (you should add all wards for all subcounties)
INSERT INTO wards (name, subcounty_id) VALUES
('Kitisuru', (SELECT id FROM subcounties WHERE name = 'Westlands')),
('Parklands/Highridge', (SELECT id FROM subcounties WHERE name = 'Westlands')),
('Karura', (SELECT id FROM subcounties WHERE name = 'Westlands')),
('Kangemi', (SELECT id FROM subcounties WHERE name = 'Westlands')),
('Mountain View', (SELECT id FROM subcounties WHERE name = 'Westlands'));
