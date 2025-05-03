-- Disable foreign key checks
PRAGMA foreign_keys = OFF;

-- Truncate case_attachments table
DELETE FROM case_attachments;

-- Truncate case_history table
DELETE FROM case_history;

-- Reset auto-increment counters
DELETE FROM sqlite_sequence WHERE name IN ('case_history', 'case_attachments');

-- Re-enable foreign key checks
PRAGMA foreign_keys = ON;

-- Verify tables are empty
SELECT COUNT(*) FROM case_history;
SELECT COUNT(*) FROM case_attachments;
