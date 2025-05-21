-- MySQL script to update branches table
-- This script is idempotent and can be run multiple times safely

-- First, check if the branches table exists
SELECT 'Checking for branches table' AS 'Status';
SELECT * FROM information_schema.tables 
WHERE table_schema = DATABASE() AND table_name = 'branches';

-- If the table doesn't exist, create it
CREATE TABLE IF NOT EXISTS branches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by) REFERENCES staff(id) ON DELETE SET NULL,
    FOREIGN KEY (updated_by) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Add address column if it doesn't exist
SET @dbname = DATABASE();
SET @tablename = 'branches';
SET @columnname = 'address';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_schema = @dbname)
      AND (table_name = @tablename)
      AND (column_name = @columnname)
  ) > 0,
  'SELECT "Address column already exists" AS Status;',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN ', @columnname, ' TEXT; SELECT "Added address column" AS Status;')
));

PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Rename branch_code to code if it exists
SET @columnname = 'branch_code';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_schema = @dbname)
      AND (table_name = @tablename)
      AND (column_name = @columnname)
  ) > 0,
  'ALTER TABLE branches CHANGE COLUMN branch_code code VARCHAR(20) NOT NULL; SELECT "Renamed branch_code to code" AS Status;',
  'SELECT "branch_code column does not exist" AS Status;'
));

PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Rename branch_name to name if it exists
SET @columnname = 'branch_name';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_schema = @dbname)
      AND (table_name = @tablename)
      AND (column_name = @columnname)
  ) > 0,
  'ALTER TABLE branches CHANGE COLUMN branch_name name VARCHAR(100) NOT NULL; SELECT "Renamed branch_name to name" AS Status;',
  'SELECT "branch_name column does not exist" AS Status;'
));

PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Drop obsolete columns if they exist
SET @columnname = 'lower_limit';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_schema = @dbname)
      AND (table_name = @tablename)
      AND (column_name = @columnname)
  ) > 0,
  'ALTER TABLE branches DROP COLUMN lower_limit; SELECT "Dropped lower_limit column" AS Status;',
  'SELECT "lower_limit column does not exist" AS Status;'
));

PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

SET @columnname = 'upper_limit';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_schema = @dbname)
      AND (table_name = @tablename)
      AND (column_name = @columnname)
  ) > 0,
  'ALTER TABLE branches DROP COLUMN upper_limit; SELECT "Dropped upper_limit column" AS Status;',
  'SELECT "upper_limit column does not exist" AS Status;'
));

PREPARE alterIfExists FROM @preparedStatement;
EXECUTE alterIfExists;
DEALLOCATE PREPARE alterIfExists;

-- Add is_active column if it doesn't exist
SET @columnname = 'is_active';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_schema = @dbname)
      AND (table_name = @tablename)
      AND (column_name = @columnname)
  ) > 0,
  'SELECT "is_active column already exists" AS Status;',
  'ALTER TABLE branches ADD COLUMN is_active BOOLEAN DEFAULT TRUE; SELECT "Added is_active column" AS Status;'
));

PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add updated_by column if it doesn't exist
SET @columnname = 'updated_by';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_schema = @dbname)
      AND (table_name = @tablename)
      AND (column_name = @columnname)
  ) > 0,
  'SELECT "updated_by column already exists" AS Status;',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN updated_by INT; ', 
         'ALTER TABLE ', @tablename, ' ADD CONSTRAINT fk_branches_updated_by ', 
         'FOREIGN KEY (updated_by) REFERENCES staff(id) ON DELETE SET NULL; ', 
         'SELECT "Added updated_by column and constraint" AS Status;')
));

PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Add updated_at column if it doesn't exist
SET @columnname = 'updated_at';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_schema = @dbname)
      AND (table_name = @tablename)
      AND (column_name = @columnname)
  ) > 0,
  'SELECT "updated_at column already exists" AS Status;',
  'ALTER TABLE branches ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP; SELECT "Added updated_at column" AS Status;'
));

PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Create indexes if they don't exist
SET @dbname = DATABASE();
SET @tablename = 'branches';
SET @indexname = 'idx_branches_code';
SET @sql = (SELECT IF(
    EXISTS(
        SELECT 1 FROM information_schema.statistics
        WHERE table_schema = @dbname
        AND table_name = @tablename
        AND index_name = @indexname
    ),
    '',
    'CREATE INDEX idx_branches_code ON branches(code)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @indexname = 'idx_branches_is_active';
SET @sql = (SELECT IF(
    EXISTS(
        SELECT 1 FROM information_schema.statistics
        WHERE table_schema = @dbname
        AND table_name = @tablename
        AND index_name = @indexname
    ),
    '',
    'CREATE INDEX idx_branches_is_active ON branches(is_active)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Show final table structure
DESCRIBE branches;

-- Show indexes on the branches table
SHOW INDEX FROM branches;

-- Show any foreign key constraints
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE
    TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'branches'
    AND REFERENCED_TABLE_NAME IS NOT NULL;
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE
    TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'branches'
    AND REFERENCED_TABLE_NAME IS NOT NULL;
