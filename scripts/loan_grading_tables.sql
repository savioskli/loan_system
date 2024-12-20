-- Create Navision-style loan grading tables

-- Create table for loan grading details
CREATE TABLE IF NOT EXISTS loan_grading (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    loan_account_no VARCHAR(20) NOT NULL,
    loan_amount DECIMAL(15,2) NOT NULL,
    outstanding_balance DECIMAL(15,2) NOT NULL,
    days_in_arrears INT NOT NULL,
    principal_in_arrears DECIMAL(15,2) NOT NULL,
    interest_in_arrears DECIMAL(15,2) NOT NULL,
    total_in_arrears DECIMAL(15,2) NOT NULL,
    classification VARCHAR(1) NOT NULL,  -- A, B, C, D, E as per Navision
    classification_date DATE NOT NULL,
    provision_rate DECIMAL(5,2) NOT NULL,  -- Percentage based on classification
    provision_amount DECIMAL(15,2) NOT NULL,
    last_payment_date DATE,
    next_payment_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Insert loan grading records
INSERT INTO loan_grading (
    client_id,
    loan_account_no,
    loan_amount,
    outstanding_balance,
    days_in_arrears,
    principal_in_arrears,
    interest_in_arrears,
    total_in_arrears,
    classification,
    classification_date,
    provision_rate,
    provision_amount,
    last_payment_date,
    next_payment_date
) 
SELECT 
    c.id,
    CONCAT('LN', LPAD(c.id, 8, '0')),  -- Generate loan account number
    CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)),
    CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.9,  -- Assume 10% paid
    CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) AS UNSIGNED),
    -- Calculate arrears based on loan amount and days
    CASE 
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 30 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.02
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 60 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.04
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 90 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.06
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 180 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.08
        ELSE CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.10
    END as principal_in_arrears,
    -- Calculate interest in arrears
    CASE 
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 30 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.01 / 12
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 60 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.02 / 12
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 90 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.03 / 12
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 180 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.04 / 12
        ELSE CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.05 / 12
    END as interest_in_arrears,
    -- Total in arrears will be calculated as principal + interest
    CASE 
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 30 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * (0.02 + CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.01 / 12)
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 60 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * (0.04 + CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.02 / 12)
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 90 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * (0.06 + CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.03 / 12)
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.days_in_arrears')) <= 180 THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * (0.08 + CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.04 / 12)
        ELSE CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * (0.10 + CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.interest_rate')) AS DECIMAL(15,2)) * 0.05 / 12)
    END as total_in_arrears,
    JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.risk_grade')) as classification,
    STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.last_payment_date')), '%Y-%m-%d') as classification_date,
    -- Provision rates as per Navision standards
    CASE 
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.risk_grade')) = 'A' THEN 1.00
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.risk_grade')) = 'B' THEN 3.00
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.risk_grade')) = 'C' THEN 20.00
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.risk_grade')) = 'D' THEN 50.00
        ELSE 100.00
    END as provision_rate,
    -- Calculate provision amount based on outstanding balance and provision rate
    CASE 
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.risk_grade')) = 'A' THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.9 * 0.01
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.risk_grade')) = 'B' THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.9 * 0.03
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.risk_grade')) = 'C' THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.9 * 0.20
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.risk_grade')) = 'D' THEN CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.9 * 0.50
        ELSE CAST(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.loan_amount')) AS DECIMAL(15,2)) * 0.9 * 1.00
    END as provision_amount,
    STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.last_payment_date')), '%Y-%m-%d') as last_payment_date,
    DATE_ADD(STR_TO_DATE(JSON_UNQUOTE(JSON_EXTRACT(c.form_data, '$.last_payment_date')), '%Y-%m-%d'), INTERVAL 30 DAY) as next_payment_date
FROM clients c
WHERE c.status = 'Defaulted';
