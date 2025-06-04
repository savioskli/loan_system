-- Add purpose and product columns to prospect_registration_data table
ALTER TABLE prospect_registration_data
ADD COLUMN purpose VARCHAR(255) DEFAULT NULL,
ADD COLUMN product VARCHAR(255) DEFAULT NULL;
