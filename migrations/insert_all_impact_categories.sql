-- We already have Agricultural Production, so let's add more categories

-- Livestock Production Impact Category
INSERT INTO `impact_categories` 
(`name`, `description`, `active`, `created_at`, `updated_at`)
VALUES 
('Livestock Production', 'Tracks the impact of loans used for livestock activities including animal purchases, feed, veterinary care, and related infrastructure. Measures increases in herd size, animal health, and production of animal products.', TRUE, NOW(), NOW());

-- Insert metrics for Livestock Production
INSERT INTO `impact_metrics` 
(`impact_category_id`, `name`, `data_type`, `unit`, `required`, `active`)
VALUES 
((SELECT id FROM `impact_categories` WHERE name = 'Livestock Production'), 'Number of Animals Purchased', 'number', 'animals', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Livestock Production'), 'Animal Type', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Livestock Production'), 'Previous Herd Size', 'number', 'animals', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Livestock Production'), 'Expected Milk Production', 'number', 'liters/month', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Livestock Production'), 'Expected Meat Production', 'number', 'kg/year', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Livestock Production'), 'Improved Housing Built', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Livestock Production'), 'Veterinary Care Improved', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Livestock Production'), 'Hired Additional Workers', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Livestock Production'), 'Number of Workers Hired', 'number', 'people', FALSE, TRUE);

-- Small Business Development Impact Category
INSERT INTO `impact_categories` 
(`name`, `description`, `active`, `created_at`, `updated_at`)
VALUES 
('Small Business Development', 'Tracks the impact of loans used for starting or expanding small businesses. Measures business growth, employment creation, revenue increases, and market expansion.', TRUE, NOW(), NOW());

-- Insert metrics for Small Business Development
INSERT INTO `impact_metrics` 
(`impact_category_id`, `name`, `data_type`, `unit`, `required`, `active`)
VALUES 
((SELECT id FROM `impact_categories` WHERE name = 'Small Business Development'), 'Business Type', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Small Business Development'), 'New Business Started', 'boolean', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Small Business Development'), 'Previous Monthly Revenue', 'number', 'currency', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Small Business Development'), 'Expected Monthly Revenue', 'number', 'currency', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Small Business Development'), 'Jobs Created', 'number', 'people', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Small Business Development'), 'New Equipment Purchased', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Small Business Development'), 'New Products/Services Offered', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Small Business Development'), 'Market Expansion', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Small Business Development'), 'Formalization Status', 'text', NULL, FALSE, TRUE);

-- Education Impact Category
INSERT INTO `impact_categories` 
(`name`, `description`, `active`, `created_at`, `updated_at`)
VALUES 
('Education', 'Tracks the impact of loans used for educational purposes including school fees, educational materials, and training programs. Measures educational attainment, skill development, and career advancement.', TRUE, NOW(), NOW());

-- Insert metrics for Education
INSERT INTO `impact_metrics` 
(`impact_category_id`, `name`, `data_type`, `unit`, `required`, `active`)
VALUES 
((SELECT id FROM `impact_categories` WHERE name = 'Education'), 'Education Level', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Education'), 'Number of Students Supported', 'number', 'students', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Education'), 'Course/Program Name', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Education'), 'Expected Completion Date', 'date', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Education'), 'Expected Qualification', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Education'), 'Career Advancement Expected', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Education'), 'Expected Income Increase', 'number', 'percentage', FALSE, TRUE);

-- Housing Improvement Impact Category
INSERT INTO `impact_categories` 
(`name`, `description`, `active`, `created_at`, `updated_at`)
VALUES 
('Housing Improvement', 'Tracks the impact of loans used for housing improvements including construction, renovation, and infrastructure upgrades. Measures improvements in living conditions, safety, and property value.', TRUE, NOW(), NOW());

-- Insert metrics for Housing Improvement
INSERT INTO `impact_metrics` 
(`impact_category_id`, `name`, `data_type`, `unit`, `required`, `active`)
VALUES 
((SELECT id FROM `impact_categories` WHERE name = 'Housing Improvement'), 'Type of Improvement', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Housing Improvement'), 'Previous Housing Condition', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Housing Improvement'), 'New Construction', 'boolean', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Housing Improvement'), 'Area Improved', 'number', 'square meters', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Housing Improvement'), 'Water Access Improved', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Housing Improvement'), 'Sanitation Improved', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Housing Improvement'), 'Electricity Access Improved', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Housing Improvement'), 'Number of Beneficiaries', 'number', 'people', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Housing Improvement'), 'Expected Property Value Increase', 'number', 'percentage', FALSE, TRUE);

-- Healthcare Impact Category
INSERT INTO `impact_categories` 
(`name`, `description`, `active`, `created_at`, `updated_at`)
VALUES 
('Healthcare', 'Tracks the impact of loans used for healthcare purposes including medical treatments, health insurance, and healthcare business development. Measures improvements in health outcomes and healthcare access.', TRUE, NOW(), NOW());

-- Insert metrics for Healthcare
INSERT INTO `impact_metrics` 
(`impact_category_id`, `name`, `data_type`, `unit`, `required`, `active`)
VALUES 
((SELECT id FROM `impact_categories` WHERE name = 'Healthcare'), 'Healthcare Purpose', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Healthcare'), 'Number of People Receiving Care', 'number', 'people', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Healthcare'), 'Type of Treatment/Service', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Healthcare'), 'Healthcare Business Started', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Healthcare'), 'Healthcare Equipment Purchased', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Healthcare'), 'Expected Health Outcome', 'text', NULL, FALSE, TRUE);

-- Renewable Energy Impact Category
INSERT INTO `impact_categories` 
(`name`, `description`, `active`, `created_at`, `updated_at`)
VALUES 
('Renewable Energy', 'Tracks the impact of loans used for renewable energy installations such as solar panels, biogas digesters, and energy-efficient appliances. Measures energy access, cost savings, and environmental benefits.', TRUE, NOW(), NOW());

-- Insert metrics for Renewable Energy
INSERT INTO `impact_metrics` 
(`impact_category_id`, `name`, `data_type`, `unit`, `required`, `active`)
VALUES 
((SELECT id FROM `impact_categories` WHERE name = 'Renewable Energy'), 'Energy System Type', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Renewable Energy'), 'System Capacity', 'number', 'kW', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Renewable Energy'), 'Previous Energy Source', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Renewable Energy'), 'Expected Monthly Energy Production', 'number', 'kWh', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Renewable Energy'), 'Expected Monthly Cost Savings', 'number', 'currency', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Renewable Energy'), 'Number of Beneficiaries', 'number', 'people', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Renewable Energy'), 'Business Use', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Renewable Energy'), 'Expected CO2 Reduction', 'number', 'kg/year', FALSE, TRUE);

-- Transportation Impact Category
INSERT INTO `impact_categories` 
(`name`, `description`, `active`, `created_at`, `updated_at`)
VALUES 
('Transportation', 'Tracks the impact of loans used for transportation assets such as vehicles for personal use or business operations. Measures mobility improvements, time savings, and business efficiency.', TRUE, NOW(), NOW());

-- Insert metrics for Transportation
INSERT INTO `impact_metrics` 
(`impact_category_id`, `name`, `data_type`, `unit`, `required`, `active`)
VALUES 
((SELECT id FROM `impact_categories` WHERE name = 'Transportation'), 'Vehicle Type', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Transportation'), 'Business Use', 'boolean', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Transportation'), 'Previous Transportation Method', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Transportation'), 'Expected Daily Travel Distance', 'number', 'km', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Transportation'), 'Expected Time Savings', 'number', 'hours/week', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Transportation'), 'Expected Revenue Increase', 'number', 'currency', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Transportation'), 'Number of Beneficiaries', 'number', 'people', TRUE, TRUE);

-- Water and Sanitation Impact Category
INSERT INTO `impact_categories` 
(`name`, `description`, `active`, `created_at`, `updated_at`)
VALUES 
('Water and Sanitation', 'Tracks the impact of loans used for water and sanitation improvements including wells, water tanks, toilets, and sewage systems. Measures access to clean water, improved sanitation, and health benefits.', TRUE, NOW(), NOW());

-- Insert metrics for Water and Sanitation
INSERT INTO `impact_metrics` 
(`impact_category_id`, `name`, `data_type`, `unit`, `required`, `active`)
VALUES 
((SELECT id FROM `impact_categories` WHERE name = 'Water and Sanitation'), 'Improvement Type', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Water and Sanitation'), 'Previous Water Source', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Water and Sanitation'), 'Previous Sanitation Facility', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Water and Sanitation'), 'Expected Water Capacity', 'number', 'liters', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Water and Sanitation'), 'Expected Time Savings', 'number', 'hours/week', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Water and Sanitation'), 'Number of Beneficiaries', 'number', 'people', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Water and Sanitation'), 'Business Use', 'boolean', NULL, FALSE, TRUE);
