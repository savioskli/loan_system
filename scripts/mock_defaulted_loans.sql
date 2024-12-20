-- Insert mock clients with loan applications in default
-- Using Navision's loan grading system:
-- Grade A: 1-30 days
-- Grade B: 31-60 days
-- Grade C: 61-90 days
-- Grade D: 91-180 days
-- Grade E: Over 180 days

-- Insert Individual Clients with defaulted loans
INSERT INTO clients (
    client_type_id,
    form_data,
    status,
    created_by,
    updated_by
) VALUES
-- Grade A clients (1-30 days)
(1, '{
    "national_id": "23456789",
    "first_name": "John",
    "last_name": "Kamau",
    "phone": "+254712345678",
    "email": "john.kamau@email.com",
    "date_of_birth": "1985-03-15",
    "gender": "M",
    "address": "Karen Estate",
    "city": "Nairobi",
    "occupation": "Software Engineer",
    "employer": "Tech Solutions Ltd",
    "monthly_income": 150000,
    "loan_amount": 500000,
    "loan_purpose": "Home Renovation",
    "loan_term": 24,
    "interest_rate": 14.5,
    "disbursement_date": "2023-11-15",
    "last_payment_date": "2023-12-10",
    "days_in_arrears": 10,
    "risk_grade": "A"
}', 'Defaulted', 1, 1),
(1, '{
    "national_id": "34567890",
    "first_name": "Mary",
    "last_name": "Wanjiku",
    "phone": "+254723456789",
    "email": "mary.wanjiku@email.com",
    "date_of_birth": "1990-07-22",
    "gender": "F",
    "address": "Kilimani Area",
    "city": "Nairobi",
    "occupation": "Accountant",
    "employer": "Financial Services Co",
    "monthly_income": 120000,
    "loan_amount": 750000,
    "loan_purpose": "Business Expansion",
    "loan_term": 36,
    "interest_rate": 16.0,
    "disbursement_date": "2023-11-10",
    "last_payment_date": "2023-12-05",
    "days_in_arrears": 15,
    "risk_grade": "A"
}', 'Defaulted', 1, 1),

-- Grade B clients (31-60 days)
(1, '{
    "national_id": "45678901",
    "first_name": "Peter",
    "last_name": "Ochieng",
    "phone": "+254734567890",
    "email": "peter.ochieng@email.com",
    "date_of_birth": "1988-11-30",
    "gender": "M",
    "address": "Westlands",
    "city": "Nairobi",
    "occupation": "Sales Manager",
    "employer": "Retail Solutions",
    "monthly_income": 200000,
    "loan_amount": 1000000,
    "loan_purpose": "Equipment Purchase",
    "loan_term": 48,
    "interest_rate": 15.5,
    "disbursement_date": "2023-10-15",
    "last_payment_date": "2023-11-10",
    "days_in_arrears": 40,
    "risk_grade": "B"
}', 'Defaulted', 1, 1),
(1, '{
    "national_id": "56789012",
    "first_name": "Sarah",
    "last_name": "Muthoni",
    "phone": "+254745678901",
    "email": "sarah.muthoni@email.com",
    "date_of_birth": "1992-04-18",
    "gender": "F",
    "address": "Lavington",
    "city": "Nairobi",
    "occupation": "Marketing Executive",
    "employer": "Media Group",
    "monthly_income": 180000,
    "loan_amount": 450000,
    "loan_purpose": "Education",
    "loan_term": 24,
    "interest_rate": 14.0,
    "disbursement_date": "2023-10-10",
    "last_payment_date": "2023-11-05",
    "days_in_arrears": 45,
    "risk_grade": "B"
}', 'Defaulted', 1, 1),

-- Grade C clients (61-90 days)
(1, '{
    "national_id": "67890123",
    "first_name": "James",
    "last_name": "Kiprop",
    "phone": "+254756789012",
    "email": "james.kiprop@email.com",
    "date_of_birth": "1987-09-25",
    "gender": "M",
    "address": "Kileleshwa",
    "city": "Nairobi",
    "occupation": "Business Owner",
    "employer": "Self Employed",
    "monthly_income": 300000,
    "loan_amount": 800000,
    "loan_purpose": "Debt Consolidation",
    "loan_term": 48,
    "interest_rate": 16.5,
    "disbursement_date": "2023-09-15",
    "last_payment_date": "2023-10-10",
    "days_in_arrears": 70,
    "risk_grade": "C"
}', 'Defaulted', 1, 1),
(1, '{
    "national_id": "78901234",
    "first_name": "Grace",
    "last_name": "Akinyi",
    "phone": "+254767890123",
    "email": "grace.akinyi@email.com",
    "date_of_birth": "1993-01-12",
    "gender": "F",
    "address": "South B",
    "city": "Nairobi",
    "occupation": "Teacher",
    "employer": "International School",
    "monthly_income": 90000,
    "loan_amount": 1200000,
    "loan_purpose": "Inventory Purchase",
    "loan_term": 36,
    "interest_rate": 15.5,
    "disbursement_date": "2023-09-10",
    "last_payment_date": "2023-10-05",
    "days_in_arrears": 75,
    "risk_grade": "C"
}', 'Defaulted', 1, 1),

-- Grade D clients (91-180 days)
(1, '{
    "national_id": "89012345",
    "first_name": "David",
    "last_name": "Njoroge",
    "phone": "+254778901234",
    "email": "david.njoroge@email.com",
    "date_of_birth": "1986-06-20",
    "gender": "M",
    "address": "Parklands",
    "city": "Nairobi",
    "occupation": "Doctor",
    "employer": "City Hospital",
    "monthly_income": 250000,
    "loan_amount": 2000000,
    "loan_purpose": "Medical Equipment",
    "loan_term": 60,
    "interest_rate": 17.0,
    "disbursement_date": "2023-08-15",
    "last_payment_date": "2023-09-10",
    "days_in_arrears": 100,
    "risk_grade": "D"
}', 'Defaulted', 1, 1),
(1, '{
    "national_id": "90123456",
    "first_name": "Alice",
    "last_name": "Wairimu",
    "phone": "+254789012345",
    "email": "alice.wairimu@email.com",
    "date_of_birth": "1991-12-05",
    "gender": "F",
    "address": "Ngong Road",
    "city": "Nairobi",
    "occupation": "Lawyer",
    "employer": "Legal Associates",
    "monthly_income": 220000,
    "loan_amount": 1500000,
    "loan_purpose": "Office Expansion",
    "loan_term": 48,
    "interest_rate": 16.0,
    "disbursement_date": "2023-08-10",
    "last_payment_date": "2023-09-05",
    "days_in_arrears": 105,
    "risk_grade": "D"
}', 'Defaulted', 1, 1),

-- Grade E clients (>180 days)
(1, '{
    "national_id": "01234567",
    "first_name": "Michael",
    "last_name": "Otieno",
    "phone": "+254790123456",
    "email": "michael.otieno@email.com",
    "date_of_birth": "1989-08-14",
    "gender": "M",
    "address": "Hurlingham",
    "city": "Nairobi",
    "occupation": "Architect",
    "employer": "Design Studios",
    "monthly_income": 170000,
    "loan_amount": 1800000,
    "loan_purpose": "Property Development",
    "loan_term": 60,
    "interest_rate": 17.5,
    "disbursement_date": "2023-05-15",
    "last_payment_date": "2023-06-10",
    "days_in_arrears": 190,
    "risk_grade": "E"
}', 'Defaulted', 1, 1);

-- Create view for loan grading analysis
CREATE OR REPLACE VIEW loan_grading_analysis AS
SELECT 
    JSON_UNQUOTE(JSON_EXTRACT(form_data, '$.risk_grade')) as risk_grade,
    COUNT(*) as loan_count,
    SUM(CAST(JSON_UNQUOTE(JSON_EXTRACT(form_data, '$.loan_amount')) AS DECIMAL(10,2))) as total_exposure,
    AVG(CAST(JSON_UNQUOTE(JSON_EXTRACT(form_data, '$.days_in_arrears')) AS DECIMAL(10,2))) as avg_days_in_arrears,
    MIN(CAST(JSON_UNQUOTE(JSON_EXTRACT(form_data, '$.days_in_arrears')) AS DECIMAL(10,2))) as min_days_in_arrears,
    MAX(CAST(JSON_UNQUOTE(JSON_EXTRACT(form_data, '$.days_in_arrears')) AS DECIMAL(10,2))) as max_days_in_arrears
FROM clients
WHERE status = 'Defaulted'
GROUP BY JSON_UNQUOTE(JSON_EXTRACT(form_data, '$.risk_grade'))
ORDER BY risk_grade;
