-- Add staff assignment fields to auction table
ALTER TABLE auction
ADD COLUMN assigned_staff_id INT,
ADD COLUMN assigned_staff_name VARCHAR(100),
ADD COLUMN supervisor_id INT,
ADD COLUMN supervisor_name VARCHAR(100);
