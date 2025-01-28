-- Loan Rescheduling Table
CREATE TABLE IF NOT EXISTS loan_rescheduling (
    id INT PRIMARY KEY AUTO_INCREMENT,
    loan_id INT NOT NULL,
    client_id INT NOT NULL,
    current_balance DECIMAL(15,2) NOT NULL,
    new_tenure INT NOT NULL,
    new_installment DECIMAL(15,2) NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    created_by INT NOT NULL,
    approved_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- Loan Refinancing Table
CREATE TABLE IF NOT EXISTS loan_refinancing (
    id INT PRIMARY KEY AUTO_INCREMENT,
    loan_id INT NOT NULL,
    client_id INT NOT NULL,
    current_balance DECIMAL(15,2) NOT NULL,
    additional_amount DECIMAL(15,2) NOT NULL,
    new_total DECIMAL(15,2) NOT NULL,
    new_tenure INT NOT NULL,
    new_installment DECIMAL(15,2) NOT NULL,
    purpose TEXT NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    created_by INT NOT NULL,
    approved_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- Settlement Plans Table
CREATE TABLE IF NOT EXISTS settlement_plans (
    id INT PRIMARY KEY AUTO_INCREMENT,
    loan_id INT NOT NULL,
    client_id INT NOT NULL,
    current_balance DECIMAL(15,2) NOT NULL,
    settlement_amount DECIMAL(15,2) NOT NULL,
    waiver_amount DECIMAL(15,2) NOT NULL,
    reason TEXT NOT NULL,
    deadline_date DATE NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected', 'Completed') DEFAULT 'Pending',
    created_by INT NOT NULL,
    approved_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);
