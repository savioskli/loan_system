-- Create form_sections table if it doesn't exist
CREATE TABLE IF NOT EXISTS `form_sections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `module` varchar(50) NOT NULL,
  `submodule` varchar(50) NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert sample form sections
INSERT INTO `form_sections` (`name`, `module`, `submodule`, `is_active`) VALUES
('General Information', 'Client Management', 'Client Registration', 1),
('Family Information', 'Client Management', 'Client Registration', 1),
('Next of Kin', 'Client Management', 'Client Registration', 1),
('Occupation', 'Client Management', 'Client Registration', 1),
('Signatories', 'Client Management', 'Client Registration', 1),
('Officials', 'Client Management', 'Client Registration', 1),
('Services', 'Client Management', 'Client Registration', 1),
('Documents', 'Client Management', 'Client Registration', 1);
