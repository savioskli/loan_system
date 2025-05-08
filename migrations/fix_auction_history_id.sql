-- Drop the foreign key constraint first
ALTER TABLE auction_history_attachments
DROP FOREIGN KEY auction_history_attachments_ibfk_1;

-- Modify the id column to be auto-increment
ALTER TABLE auction_history MODIFY COLUMN id INTEGER AUTO_INCREMENT;

-- Re-add the foreign key constraint
ALTER TABLE auction_history_attachments
ADD CONSTRAINT auction_history_attachments_ibfk_1
FOREIGN KEY (history_id) REFERENCES auction_history(id);
