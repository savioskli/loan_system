-- Create branch_limits table
CREATE TABLE IF NOT EXISTS branch_limits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NOT NULL,
    min_amount DECIMAL(15,2) NOT NULL,
    max_amount DECIMAL(15,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (branch_id) REFERENCES branches(id),
    FOREIGN KEY (created_by) REFERENCES staff(id),
    FOREIGN KEY (updated_by) REFERENCES staff(id),
    CONSTRAINT unique_active_branch UNIQUE (branch_id, is_active),
    CONSTRAINT min_less_than_max CHECK (min_amount <= max_amount)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add index for faster lookups
CREATE INDEX idx_branch_limits_branch ON branch_limits(branch_id);
CREATE INDEX idx_branch_limits_active ON branch_limits(is_active);

-- Add trigger to prevent multiple active limits per branch
DELIMITER //
CREATE TRIGGER before_branch_limit_insert 
BEFORE INSERT ON branch_limits
FOR EACH ROW
BEGIN
    IF NEW.is_active = TRUE THEN
        -- Check if there's already an active limit for this branch
        IF EXISTS (SELECT 1 FROM branch_limits WHERE branch_id = NEW.branch_id AND is_active = TRUE) THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'An active limit already exists for this branch';
        END IF;
    END IF;
END//
DELIMITER ;
