CREATE TABLE guarantor_claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guarantor_name VARCHAR(255) NOT NULL,
    borrower_name VARCHAR(255) NOT NULL,
    guarantor_contact VARCHAR(50),
    borrower_contact VARCHAR(50),
    amount_paid DECIMAL(15, 2) NOT NULL,
    claim_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pending' NOT NULL,
    claim_description TEXT,
    guarantor_id INT,
    loan_id INT,
    FOREIGN KEY (guarantor_id) REFERENCES guarantors(id),
    FOREIGN KEY (loan_id) REFERENCES loans(id)
);
