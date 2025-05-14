-- Insert Agriculture Impact Category
INSERT INTO `impact_categories` 
(`name`, `description`, `active`, `created_at`, `updated_at`)
VALUES 
('Agricultural Production', 'Tracks the impact of loans used for agricultural activities including crop production, farm equipment purchases, and land development. Measures increases in yield, acreage cultivated, and overall farm productivity.', TRUE, NOW(), NOW());

-- Insert related metrics for Agricultural Production
INSERT INTO `impact_metrics` 
(`impact_category_id`, `name`, `data_type`, `unit`, `required`, `active`)
VALUES 
((SELECT id FROM `impact_categories` WHERE name = 'Agricultural Production'), 'Land Area Cultivated', 'number', 'acres', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Agricultural Production'), 'Crop Type', 'text', NULL, TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Agricultural Production'), 'Previous Yield', 'number', 'kg/acre', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Agricultural Production'), 'Expected Yield', 'number', 'kg/acre', TRUE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Agricultural Production'), 'Farm Equipment Purchased', 'text', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Agricultural Production'), 'Hired Additional Workers', 'boolean', NULL, FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Agricultural Production'), 'Number of Workers Hired', 'number', 'people', FALSE, TRUE),
((SELECT id FROM `impact_categories` WHERE name = 'Agricultural Production'), 'Irrigation System Improved', 'boolean', NULL, FALSE, TRUE);
