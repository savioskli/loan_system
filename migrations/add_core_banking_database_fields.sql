-- Add database_name and selected_tables columns to core_banking_systems table
ALTER TABLE core_banking_systems
ADD COLUMN database_name VARCHAR(100) NULL AFTER headers,
ADD COLUMN selected_tables TEXT NULL AFTER database_name;
