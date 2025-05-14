-- Create loan_impact table
CREATE TABLE IF NOT EXISTS `loan_impact` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loan_id` int(11) NOT NULL,
  `impact_category_id` int(11) NOT NULL,
  `submitted_by` int(11) NOT NULL,
  `submission_date` datetime NOT NULL,
  `verification_status` varchar(20) NOT NULL DEFAULT 'Pending',
  `verification_notes` text,
  `verified_by` int(11) DEFAULT NULL,
  `verification_date` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `loan_id_idx` (`loan_id`),
  KEY `impact_category_id_idx` (`impact_category_id`),
  KEY `submitted_by_idx` (`submitted_by`),
  KEY `verified_by_idx` (`verified_by`),
  CONSTRAINT `fk_loan_impact_category` FOREIGN KEY (`impact_category_id`) REFERENCES `impact_categories` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_loan_impact_submitter` FOREIGN KEY (`submitted_by`) REFERENCES `staff` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_loan_impact_verifier` FOREIGN KEY (`verified_by`) REFERENCES `staff` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create impact_values table
CREATE TABLE IF NOT EXISTS `impact_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loan_impact_id` int(11) NOT NULL,
  `impact_metric_id` int(11) NOT NULL,
  `value` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `loan_impact_id_idx` (`loan_impact_id`),
  KEY `impact_metric_id_idx` (`impact_metric_id`),
  CONSTRAINT `fk_impact_values_loan_impact` FOREIGN KEY (`loan_impact_id`) REFERENCES `loan_impact` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_impact_values_metric` FOREIGN KEY (`impact_metric_id`) REFERENCES `impact_metrics` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create impact_evidence table
CREATE TABLE IF NOT EXISTS `impact_evidence` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `loan_impact_id` int(11) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `uploaded_by` int(11) NOT NULL,
  `upload_date` datetime NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `loan_impact_id_idx` (`loan_impact_id`),
  KEY `uploaded_by_idx` (`uploaded_by`),
  CONSTRAINT `fk_impact_evidence_loan_impact` FOREIGN KEY (`loan_impact_id`) REFERENCES `loan_impact` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `fk_impact_evidence_uploader` FOREIGN KEY (`uploaded_by`) REFERENCES `staff` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create uploads directory for impact evidence
CREATE TABLE IF NOT EXISTS `impact_metrics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `impact_category_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `data_type` varchar(20) NOT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `required` tinyint(1) NOT NULL DEFAULT '0',
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `impact_category_id_idx` (`impact_category_id`),
  CONSTRAINT `fk_impact_metrics_category` FOREIGN KEY (`impact_category_id`) REFERENCES `impact_categories` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
