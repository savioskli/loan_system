-- Insert system reference fields
INSERT INTO system_reference_fields (code, name, description, is_active) VALUES
('CLIENT_TYPE', 'Client Type', 'Types of clients in the system', TRUE),
('COUNTY', 'County', 'Counties in Kenya', TRUE),
('SUBCOUNTY', 'Sub County', 'Sub Counties in Kenya', TRUE),
('STATUS', 'Status', 'General status values', TRUE);

-- Insert client types
INSERT INTO system_reference_values (field_id, value, label, is_active) VALUES
((SELECT id FROM system_reference_fields WHERE code = 'CLIENT_TYPE'), 'INDIVIDUAL', 'Individual', TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'CLIENT_TYPE'), 'GROUP', 'Group', TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'CLIENT_TYPE'), 'CORPORATE', 'Corporate', TRUE);

-- Insert sample counties
INSERT INTO system_reference_values (field_id, value, label, is_active) VALUES
((SELECT id FROM system_reference_fields WHERE code = 'COUNTY'), 'NAIROBI', 'Nairobi', TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'COUNTY'), 'MOMBASA', 'Mombasa', TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'COUNTY'), 'KISUMU', 'Kisumu', TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'COUNTY'), 'NAKURU', 'Nakuru', TRUE);

-- Insert sample sub-counties with parent counties
INSERT INTO system_reference_values (field_id, value, label, parent_value_id, is_active) VALUES
((SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTY'), 'WESTLANDS', 'Westlands', 
 (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTY') AND value = 'NAIROBI'), TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTY'), 'DAGORETTI', 'Dagoretti', 
 (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTY') AND value = 'NAIROBI'), TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTY'), 'NYALI', 'Nyali', 
 (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTY') AND value = 'MOMBASA'), TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'SUBCOUNTY'), 'KISAUNI', 'Kisauni', 
 (SELECT id FROM system_reference_values WHERE field_id = (SELECT id FROM system_reference_fields WHERE code = 'COUNTY') AND value = 'MOMBASA'), TRUE);

-- Insert status values
INSERT INTO system_reference_values (field_id, value, label, is_active) VALUES
((SELECT id FROM system_reference_fields WHERE code = 'STATUS'), 'ACTIVE', 'Active', TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'STATUS'), 'INACTIVE', 'Inactive', TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'STATUS'), 'PENDING', 'Pending', TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'STATUS'), 'COMPLETED', 'Completed', TRUE),
((SELECT id FROM system_reference_fields WHERE code = 'STATUS'), 'CANCELLED', 'Cancelled', TRUE);
