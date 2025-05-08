-- First, create new attachments table
CREATE TABLE auction_history_attachments_new (
    id INTEGER PRIMARY KEY,
    history_id INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Copy attachments data
INSERT INTO auction_history_attachments_new
SELECT * FROM auction_history_attachments;

-- Create new auction history table
CREATE TABLE auction_history_new (
    id INTEGER PRIMARY KEY,
    auction_id INTEGER NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    action_date DATETIME NOT NULL,
    notes TEXT,
    status VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (auction_id) REFERENCES auction(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Copy auction history data
INSERT INTO auction_history_new (
    id,
    auction_id,
    action_type,  -- New column name
    action_date,
    notes,
    status,
    created_at,
    created_by
)
SELECT 
    id,
    auction_id,
    action,      -- Old column name
    action_date,
    notes,
    status,
    created_at,
    created_by
FROM auction_history;

-- Drop old tables (order matters due to FK constraints)
DROP TABLE auction_history_attachments;
DROP TABLE auction_history;

-- Rename new tables
ALTER TABLE auction_history_new RENAME TO auction_history;
ALTER TABLE auction_history_attachments_new RENAME TO auction_history_attachments;

-- Add back the foreign key constraint to attachments
ALTER TABLE auction_history_attachments
ADD CONSTRAINT auction_history_attachments_ibfk_1
FOREIGN KEY (history_id) REFERENCES auction_history(id) ON DELETE CASCADE;
