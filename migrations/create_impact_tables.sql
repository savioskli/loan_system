-- Create impact_categories table
CREATE TABLE IF NOT EXISTS `impact_categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `description` TEXT,
    `active` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create impact_metrics table for defining metrics for each category
CREATE TABLE IF NOT EXISTS `impact_metrics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `impact_category_id` INT NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `data_type` VARCHAR(50) NOT NULL, -- number, text, boolean, date, etc.
    `unit` VARCHAR(50) NULL, -- e.g., "cattle", "acres", "businesses"
    `required` BOOLEAN DEFAULT FALSE,
    `active` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`impact_category_id`) REFERENCES `impact_categories`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create loan_impact table to track impact for specific loans
CREATE TABLE IF NOT EXISTS `loan_impact` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `loan_id` INT NOT NULL,
    `impact_category_id` INT NOT NULL,
    `status` VARCHAR(50) DEFAULT 'pending', -- pending, verified, rejected
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `verified_by` INT NULL,
    `verified_at` TIMESTAMP NULL,
    FOREIGN KEY (`impact_category_id`) REFERENCES `impact_categories`(`id`),
    FOREIGN KEY (`loan_id`) REFERENCES `loans`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create impact_values table to store actual impact metric values
CREATE TABLE IF NOT EXISTS `impact_values` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `loan_impact_id` INT NOT NULL,
    `impact_metric_id` INT NOT NULL,
    `value_text` TEXT NULL,
    `value_number` DECIMAL(15,2) NULL,
    `value_boolean` BOOLEAN NULL,
    `value_date` DATE NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`loan_impact_id`) REFERENCES `loan_impact`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`impact_metric_id`) REFERENCES `impact_metrics`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create impact_evidence table to store evidence files
CREATE TABLE IF NOT EXISTS `impact_evidence` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `loan_impact_id` INT NOT NULL,
    `evidence_type` VARCHAR(50) NOT NULL, -- photo, document, video, etc.
    `file_path` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `uploaded_by` INT NOT NULL,
    `uploaded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`loan_impact_id`) REFERENCES `loan_impact`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
