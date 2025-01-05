-- Drop the foreign key constraint first
ALTER TABLE correspondence DROP FOREIGN KEY correspondence_ibfk_2;

-- Then drop the loan_id column
ALTER TABLE correspondence DROP COLUMN loan_id;
