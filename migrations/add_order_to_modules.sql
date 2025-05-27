-- Add order column to modules table
ALTER TABLE modules ADD COLUMN `order` INT DEFAULT 0;

-- Update order based on id for existing modules
UPDATE modules SET `order` = id WHERE `order` IS NULL;
