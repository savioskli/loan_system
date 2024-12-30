from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import random

app = Flask(__name__)
CORS(app)

# Mock data for different core banking systems
MOCK_DATA = {
    'navision': {
        'tables': [
            {
                'name': 'Customer',
                'description': 'Contains customer/client information including personal details and contact information',
                'fields': [
                    {'name': 'No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Name', 'type': 'Text[100]', 'description': 'Customer name'},
                    {'name': 'Address', 'type': 'Text[100]', 'description': 'Customer address'},
                    {'name': 'Phone_No_', 'type': 'Text[30]', 'description': 'Phone number'},
                    {'name': 'E_Mail', 'type': 'Text[80]', 'description': 'Email address'}
                ]
            },
            {
                'name': 'Loan',
                'description': 'Contains loan account information including amounts, terms, and status',
                'fields': [
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Loan_Amount', 'type': 'Decimal', 'description': 'Original loan amount'},
                    {'name': 'Outstanding_Balance', 'type': 'Decimal', 'description': 'Current outstanding balance'},
                    {'name': 'Status', 'type': 'Option', 'description': 'Loan status (Active/Closed/Default)'}
                ]
            },
            {
                'name': 'LoanApplication',
                'description': 'Contains loan application details and approval workflow',
                'fields': [
                    {'name': 'Application_No_', 'type': 'Code[20]', 'description': 'Application number'},
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Application_Date', 'type': 'Date', 'description': 'Application date'},
                    {'name': 'Status', 'type': 'Option', 'description': 'Application status'}
                ]
            },
            {
                'name': 'Collateral',
                'description': 'Contains information about loan collaterals and their valuation',
                'fields': [
                    {'name': 'Collateral_No_', 'type': 'Code[20]', 'description': 'Collateral number'},
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Type', 'type': 'Option', 'description': 'Type of collateral'},
                    {'name': 'Value', 'type': 'Decimal', 'description': 'Collateral value'}
                ]
            },
            {
                'name': 'Payment',
                'description': 'Contains loan payment history and schedules',
                'fields': [
                    {'name': 'Entry_No_', 'type': 'Integer', 'description': 'Payment entry number'},
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Payment_Date', 'type': 'Date', 'description': 'Payment date'},
                    {'name': 'Amount', 'type': 'Decimal', 'description': 'Payment amount'}
                ]
            },
            {
                'name': 'Guarantor',
                'description': 'Contains information about loan guarantors and their relationships with customers',
                'fields': [
                    {'name': 'Guarantor_No_', 'type': 'Code[20]', 'description': 'Guarantor unique identifier'},
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer being guaranteed'},
                    {'name': 'Name', 'type': 'Text[100]', 'description': 'Guarantor full name'},
                    {'name': 'ID_No_', 'type': 'Text[20]', 'description': 'National ID number'},
                    {'name': 'Phone_No_', 'type': 'Text[30]', 'description': 'Contact phone number'},
                    {'name': 'Email', 'type': 'Text[80]', 'description': 'Email address'},
                    {'name': 'Relationship', 'type': 'Option', 'description': 'Relationship to customer'},
                    {'name': 'Occupation', 'type': 'Text[50]', 'description': 'Guarantor occupation'},
                    {'name': 'Monthly_Income', 'type': 'Decimal', 'description': 'Guarantor monthly income'},
                    {'name': 'Status', 'type': 'Option', 'description': 'Status (Active/Inactive)'}
                ]
            },
            {
                'name': 'Loan_Grading',
                'description': 'Contains loan classification and provisioning details as per CBK guidelines',
                'fields': [
                    {'name': 'Entry_No_', 'type': 'Integer', 'description': 'Entry number (Primary Key)'},
                    {'name': 'Loan_Account_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Customer_Name', 'type': 'Text[100]', 'description': 'Customer name'},
                    {'name': 'Loan_Amount', 'type': 'Decimal', 'description': 'Original loan amount'},
                    {'name': 'Days_In_Arrears', 'type': 'Integer', 'description': 'Number of days payment is overdue'},
                    {'name': 'Classification', 'type': 'Option', 'description': 'Loan classification based on days in arrears',
                     'options': [
                        {'code': 'NORMAL', 'description': 'Performing Loans - Payments up to date or overdue by less than 30 days'},
                        {'code': 'WATCH', 'description': 'Special Mention - Payments overdue by 31 to 90 days'},
                        {'code': 'SUBSTANDARD', 'description': 'Payments overdue by 91 to 180 days'},
                        {'code': 'DOUBTFUL', 'description': 'Payments overdue by 181 to 360 days'},
                        {'code': 'LOSS', 'description': 'Non-Performing - Payments overdue by more than 360 days'}
                    ]},
                    {'name': 'Provision_Rate', 'type': 'Decimal', 'description': 'Required provision percentage based on classification'}
                ],
                'sample_data': [
                    {
                        'Entry_No_': 1,
                        'Loan_Account_No_': 'LN00000001',
                        'Customer_Name': 'John Kamau',
                        'Loan_Amount': 500000.00,
                        'Days_In_Arrears': 0,
                        'Classification': 'NORMAL',
                        'Provision_Rate': 1
                    },
                    {
                        'Entry_No_': 2,
                        'Loan_Account_No_': 'LN00000002',
                        'Customer_Name': 'Jane Wanjiku',
                        'Loan_Amount': 750000.00,
                        'Days_In_Arrears': 45,
                        'Classification': 'WATCH',
                        'Provision_Rate': 3
                    },
                    {
                        'Entry_No_': 3,
                        'Loan_Account_No_': 'LN00000003',
                        'Customer_Name': 'Peter Omondi',
                        'Loan_Amount': 1000000.00,
                        'Days_In_Arrears': 120,
                        'Classification': 'SUBSTANDARD',
                        'Provision_Rate': 20
                    },
                    {
                        'Entry_No_': 4,
                        'Loan_Account_No_': 'LN00000004',
                        'Customer_Name': 'Mary Muthoni',
                        'Loan_Amount': 300000.00,
                        'Days_In_Arrears': 250,
                        'Classification': 'DOUBTFUL',
                        'Provision_Rate': 50
                    },
                    {
                        'Entry_No_': 5,
                        'Loan_Account_No_': 'LN00000005',
                        'Customer_Name': 'James Kiprop',
                        'Loan_Amount': 1500000.00,
                        'Days_In_Arrears': 400,
                        'Classification': 'LOSS',
                        'Provision_Rate': 100
                    }
                ]
            }
        ]
    },
    'brnet': {
        'tables': [
            {
                'name': 'CIF',
                'description': 'Customer Information File with detailed client records',
                'fields': [
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Name', 'type': 'Text[100]', 'description': 'Customer name'},
                    {'name': 'Address', 'type': 'Text[100]', 'description': 'Customer address'},
                    {'name': 'Phone_No_', 'type': 'Text[30]', 'description': 'Phone number'},
                    {'name': 'E_Mail', 'type': 'Text[80]', 'description': 'Email address'}
                ]
            },
            {
                'name': 'LOAN_MASTER',
                'description': 'Master table for all loan accounts',
                'fields': [
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Loan_Amount', 'type': 'Decimal', 'description': 'Original loan amount'},
                    {'name': 'Outstanding_Balance', 'type': 'Decimal', 'description': 'Current outstanding balance'},
                    {'name': 'Status', 'type': 'Option', 'description': 'Loan status (Active/Closed/Default)'}
                ]
            },
            {
                'name': 'LOAN_APPLICATION',
                'description': 'Loan application processing and workflow',
                'fields': [
                    {'name': 'Application_No_', 'type': 'Code[20]', 'description': 'Application number'},
                    {'name': 'Customer_No_', 'type': 'Code[20]', 'description': 'Customer number'},
                    {'name': 'Application_Date', 'type': 'Date', 'description': 'Application date'},
                    {'name': 'Status', 'type': 'Option', 'description': 'Application status'}
                ]
            },
            {
                'name': 'COLLATERAL_REGISTER',
                'description': 'Registry of all loan securities and collaterals',
                'fields': [
                    {'name': 'Collateral_No_', 'type': 'Code[20]', 'description': 'Collateral number'},
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Type', 'type': 'Option', 'description': 'Type of collateral'},
                    {'name': 'Value', 'type': 'Decimal', 'description': 'Collateral value'}
                ]
            },
            {
                'name': 'REPAYMENT_SCHEDULE',
                'description': 'Loan repayment schedules and history',
                'fields': [
                    {'name': 'Entry_No_', 'type': 'Integer', 'description': 'Payment entry number'},
                    {'name': 'Loan_No_', 'type': 'Code[20]', 'description': 'Loan account number'},
                    {'name': 'Payment_Date', 'type': 'Date', 'description': 'Payment date'},
                    {'name': 'Amount', 'type': 'Decimal', 'description': 'Payment amount'}
                ]
            }
        ]
    }
}

# Mock client data
MOCK_CLIENTS = [
    {
        'id': 'CUS001',
        'name': 'Wanjiku Kamau',
        'phone': '+254722000001',
        'email': 'wanjiku.kamau@example.com',
        'loans': [
            {
                'account_no': 'LN001',
                'amount': 50000,
                'balance': 45000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA001',
                'name': 'Njeri Mwangi',
                'id_no': '12345678',
                'phone_no': '+254722000099',
                'email': 'njeri.mwangi@example.com',
                'relationship': 'Sister',
                'occupation': 'Teacher',
                'monthly_income': 75000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS002',
        'name': 'Omondi Otieno',
        'phone': '+254722000002',
        'email': 'omondi.otieno@example.com',
        'loans': [
            {
                'account_no': 'LN002',
                'amount': 100000,
                'balance': 80000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA002',
                'name': 'Kipchoge Kipruto',
                'id_no': '87654321',
                'phone_no': '+254722000003',
                'email': 'kipchoge.kipruto@example.com',
                'relationship': 'Business Partner',
                'occupation': 'Business Owner',
                'monthly_income': 120000,
                'status': 'Active'
            },
            {
                'guarantor_no': 'GUA003',
                'name': 'Akinyi Odhiambo',
                'id_no': '23456789',
                'phone_no': '+254722000088',
                'email': 'akinyi.odhiambo@example.com',
                'relationship': 'Spouse',
                'occupation': 'Accountant',
                'monthly_income': 90000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS003',
        'name': 'Hassan Ali Mohammed',
        'phone': '+254722000004',
        'email': 'hassan.mohammed@example.com',
        'loans': [
            {
                'account_no': 'LN003',
                'amount': 150000,
                'balance': 120000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA004',
                'name': 'Fatuma Omar',
                'id_no': '34567890',
                'phone_no': '+254722000005',
                'email': 'fatuma.omar@example.com',
                'relationship': 'Business Partner',
                'occupation': 'Shop Owner',
                'monthly_income': 85000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS004',
        'name': 'Mutua Musyoka',
        'phone': '+254722000006',
        'email': 'mutua.musyoka@example.com',
        'loans': [
            {
                'account_no': 'LN004',
                'amount': 75000,
                'balance': 60000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA005',
                'name': 'Muthoni Njoroge',
                'id_no': '45678901',
                'phone_no': '+254722000007',
                'email': 'muthoni.njoroge@example.com',
                'relationship': 'Cousin',
                'occupation': 'Civil Servant',
                'monthly_income': 95000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS005',
        'name': 'Amina Hussein',
        'phone': '+254722000008',
        'email': 'amina.hussein@example.com',
        'loans': [
            {
                'account_no': 'LN005',
                'amount': 200000,
                'balance': 180000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA006',
                'name': 'Salim Abdullah',
                'id_no': '56789012',
                'phone_no': '+254722000009',
                'email': 'salim.abdullah@example.com',
                'relationship': 'Brother',
                'occupation': 'Doctor',
                'monthly_income': 150000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS006',
        'name': 'Kipkorir Sang',
        'phone': '+254722000010',
        'email': 'kipkorir.sang@example.com',
        'loans': [
            {
                'account_no': 'LN006',
                'amount': 300000,
                'balance': 250000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA007',
                'name': 'Cherono Koech',
                'id_no': '67890123',
                'phone_no': '+254722000011',
                'email': 'cherono.koech@example.com',
                'relationship': 'Sister',
                'occupation': 'Engineer',
                'monthly_income': 130000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS007',
        'name': 'Atieno Adhiambo',
        'phone': '+254722000012',
        'email': 'atieno.adhiambo@example.com',
        'loans': [
            {
                'account_no': 'LN007',
                'amount': 80000,
                'balance': 65000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA008',
                'name': 'Owino Okoth',
                'id_no': '78901234',
                'phone_no': '+254722000013',
                'email': 'owino.okoth@example.com',
                'relationship': 'Uncle',
                'occupation': 'Teacher',
                'monthly_income': 70000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS008',
        'name': 'Njuguna Kariuki',
        'phone': '+254722000014',
        'email': 'njuguna.kariuki@example.com',
        'loans': [
            {
                'account_no': 'LN008',
                'amount': 250000,
                'balance': 200000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA009',
                'name': 'Wambui Githinji',
                'id_no': '89012345',
                'phone_no': '+254722000015',
                'email': 'wambui.githinji@example.com',
                'relationship': 'Business Partner',
                'occupation': 'Business Owner',
                'monthly_income': 180000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS009',
        'name': 'Ahmed Ibrahim',
        'phone': '+254722000016',
        'email': 'ahmed.ibrahim@example.com',
        'loans': [
            {
                'account_no': 'LN009',
                'amount': 175000,
                'balance': 150000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA010',
                'name': 'Halima Said',
                'id_no': '90123456',
                'phone_no': '+254722000017',
                'email': 'halima.said@example.com',
                'relationship': 'Sister',
                'occupation': 'Nurse',
                'monthly_income': 85000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS010',
        'name': 'Kimani Ngugi',
        'phone': '+254722000018',
        'email': 'kimani.ngugi@example.com',
        'loans': [
            {
                'account_no': 'LN010',
                'amount': 400000,
                'balance': 380000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA011',
                'name': 'Nyambura Maina',
                'id_no': '01234567',
                'phone_no': '+254722000019',
                'email': 'nyambura.maina@example.com',
                'relationship': 'Spouse',
                'occupation': 'Lawyer',
                'monthly_income': 200000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS011',
        'name': 'Wekesa Wafula',
        'phone': '+254722000020',
        'email': 'wekesa.wafula@example.com',
        'loans': [
            {
                'account_no': 'LN011',
                'amount': 120000,
                'balance': 100000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA012',
                'name': 'Nafula Simiyu',
                'id_no': '11234567',
                'phone_no': '+254722000021',
                'email': 'nafula.simiyu@example.com',
                'relationship': 'Sister',
                'occupation': 'Pharmacist',
                'monthly_income': 110000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS012',
        'name': 'Kibet Rotich',
        'phone': '+254722000022',
        'email': 'kibet.rotich@example.com',
        'loans': [
            {
                'account_no': 'LN012',
                'amount': 280000,
                'balance': 250000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA013',
                'name': 'Chebet Rono',
                'id_no': '21234567',
                'phone_no': '+254722000023',
                'email': 'chebet.rono@example.com',
                'relationship': 'Cousin',
                'occupation': 'Software Developer',
                'monthly_income': 160000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS013',
        'name': 'Juma Ochieng',
        'phone': '+254722000024',
        'email': 'juma.ochieng@example.com',
        'loans': [
            {
                'account_no': 'LN013',
                'amount': 90000,
                'balance': 75000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA014',
                'name': 'Onyango Odongo',
                'id_no': '31234567',
                'phone_no': '+254722000025',
                'email': 'onyango.odongo@example.com',
                'relationship': 'Brother',
                'occupation': 'Lecturer',
                'monthly_income': 140000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS014',
        'name': 'Muthama Kyalo',
        'phone': '+254722000026',
        'email': 'muthama.kyalo@example.com',
        'loans': [
            {
                'account_no': 'LN014',
                'amount': 150000,
                'balance': 130000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA015',
                'name': 'Mutinda Muema',
                'id_no': '41234567',
                'phone_no': '+254722000027',
                'email': 'mutinda.muema@example.com',
                'relationship': 'Business Partner',
                'occupation': 'Contractor',
                'monthly_income': 170000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS015',
        'name': 'Aisha Mohamed',
        'phone': '+254722000028',
        'email': 'aisha.mohamed@example.com',
        'loans': [
            {
                'account_no': 'LN015',
                'amount': 220000,
                'balance': 200000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA016',
                'name': 'Zainab Hassan',
                'id_no': '51234567',
                'phone_no': '+254722000029',
                'email': 'zainab.hassan@example.com',
                'relationship': 'Sister',
                'occupation': 'Dentist',
                'monthly_income': 190000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS016',
        'name': 'Kiprop Kemboi',
        'phone': '+254722000030',
        'email': 'kiprop.kemboi@example.com',
        'loans': [
            {
                'account_no': 'LN016',
                'amount': 350000,
                'balance': 320000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA017',
                'name': 'Kiptoo Bett',
                'id_no': '61234567',
                'phone_no': '+254722000031',
                'email': 'kiptoo.bett@example.com',
                'relationship': 'Brother',
                'occupation': 'Architect',
                'monthly_income': 180000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS017',
        'name': 'Nyokabi Muchiri',
        'phone': '+254722000032',
        'email': 'nyokabi.muchiri@example.com',
        'loans': [
            {
                'account_no': 'LN017',
                'amount': 180000,
                'balance': 160000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA018',
                'name': 'Waithera Ndung\'u',
                'id_no': '71234567',
                'phone_no': '+254722000033',
                'email': 'waithera.ndungu@example.com',
                'relationship': 'Business Partner',
                'occupation': 'Real Estate Agent',
                'monthly_income': 200000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS018',
        'name': 'Omar Abdallah',
        'phone': '+254722000034',
        'email': 'omar.abdallah@example.com',
        'loans': [
            {
                'account_no': 'LN018',
                'amount': 270000,
                'balance': 250000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA019',
                'name': 'Yusuf Mahmoud',
                'id_no': '81234567',
                'phone_no': '+254722000035',
                'email': 'yusuf.mahmoud@example.com',
                'relationship': 'Business Partner',
                'occupation': 'Import/Export Trader',
                'monthly_income': 250000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS019',
        'name': 'Mwangi Githae',
        'phone': '+254722000036',
        'email': 'mwangi.githae@example.com',
        'loans': [
            {
                'account_no': 'LN019',
                'amount': 420000,
                'balance': 400000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA020',
                'name': 'Njoroge Kimani',
                'id_no': '91234567',
                'phone_no': '+254722000037',
                'email': 'njoroge.kimani@example.com',
                'relationship': 'Business Partner',
                'occupation': 'Factory Owner',
                'monthly_income': 300000,
                'status': 'Active'
            }
        ]
    },
    {
        'id': 'CUS020',
        'name': 'Awino Okello',
        'phone': '+254722000038',
        'email': 'awino.okello@example.com',
        'loans': [
            {
                'account_no': 'LN020',
                'amount': 160000,
                'balance': 140000,
                'status': 'Active'
            }
        ],
        'guarantors': [
            {
                'guarantor_no': 'GUA021',
                'name': 'Akoth Owuor',
                'id_no': '10123456',
                'phone_no': '+254722000039',
                'email': 'akoth.owuor@example.com',
                'relationship': 'Sister',
                'occupation': 'Bank Manager',
                'monthly_income': 220000,
                'status': 'Active'
            }
        ]
    }
]

# Mock correspondence data
MOCK_CORRESPONDENCE = {
    'CUS001': [
        {
            'id': 'COR001',
            'type': 'email',
            'subject': 'Loan Approval',
            'content': 'Your loan has been approved.',
            'date': '2023-12-20T10:30:00',
            'status': 'sent'
        },
        {
            'id': 'COR002',
            'type': 'sms',
            'content': 'Payment reminder: Your loan payment is due in 5 days.',
            'date': '2023-12-22T09:00:00',
            'status': 'sent'
        }
    ],
    'CUS002': [
        {
            'id': 'COR003',
            'type': 'call',
            'content': 'Discussed payment schedule',
            'date': '2023-12-21T14:15:00',
            'duration': '00:10:23',
            'status': 'completed'
        }
    ]
}

@app.route('/api/beta/companies/metadata', methods=['GET'])
def navision_tables():
    # Check basic auth
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != 'admin123':
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check database name
    database = request.headers.get('Database')
    if not database or database != 'navision_db':
        return jsonify({'error': 'Invalid or missing database name'}), 400
    
    # Create simplified table metadata
    tables = [
        {'name': table['name'], 'description': table['description']} 
        for table in MOCK_DATA['navision']['tables']
    ]
    
    # Simulate some processing time
    time.sleep(0.5)
    return jsonify({'value': tables})

@app.route('/api/v1/health', methods=['GET'])
def navision_health():
    # Check basic auth
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != 'admin123':
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({'status': 'healthy', 'message': 'Navision core banking system is running'})

@app.route('/api/schema/tables', methods=['GET'])
def brnet_tables():
    # Check for API key
    api_key = request.headers.get('Authorization')
    if not api_key or not api_key.startswith('Bearer '):
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    # Simulate some processing time
    time.sleep(0.5)
    return jsonify(MOCK_DATA['brnet']['tables'])

@app.route('/api/health', methods=['GET'])
def brnet_health():
    # Check for API key
    api_key = request.headers.get('Authorization')
    if not api_key or not api_key.startswith('Bearer '):
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    return jsonify({'status': 'healthy', 'message': 'BR.NET core banking system is running'})

@app.route('/api/beta/companies/loan-grading', methods=['GET'])
def loan_grading():
    # Simulate authentication check
    auth = request.authorization
    if not auth or auth.username != 'admin' or auth.password != 'admin123':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Check database header
    if request.headers.get('Database') != 'navision_db':
        return jsonify({'error': 'Invalid database'}), 400

    # Generate mock loan data
    kenyan_names = [
        "Wanjiku", "Kamau", "Ochieng", "Muthoni", "Kiprop", "Akinyi", "Otieno", "Njeri", "Kimani", "Adhiambo",
        "Omondi", "Njoroge", "Wambui", "Kariuki", "Auma", "Maina", "Nyambura", "Kibet", "Onyango", "Gathoni",
        "Mutua", "Awuor", "Gitau", "Wangari", "Korir", "Atieno", "Ngugi", "Waithera", "Ruto", "Nekesa",
        "Karanja", "Akoth", "Ndungu", "Wanjiru", "Sang", "Achieng", "Mwangi", "Moraa", "Chebet", "Odhiambo",
        "Njuguna", "Nyokabi", "Rotich", "Anyango", "Gicheru", "Kerubo", "Kiptoo", "Aoko", "Macharia", "Kemunto"
    ]
    first_names = [
        "John", "Jane", "Peter", "Mary", "James", "Grace", "David", "Faith", "Daniel", "Hope",
        "Samuel", "Joy", "Joseph", "Peace", "Michael", "Mercy", "George", "Charity", "Paul", "Blessing",
        "Stephen", "Elizabeth", "Charles", "Catherine", "Francis", "Christine", "Thomas", "Caroline", "Anthony", "Esther",
        "Robert", "Sarah", "Richard", "Ruth", "William", "Rachel", "Edward", "Rebecca", "Henry", "Rose",
        "Philip", "Victoria", "Dennis", "Lucy", "Patrick", "Anne", "Bernard", "Alice", "Vincent", "Agnes"
    ]

    # Generate 120 loan records
    loan_data = []
    for i in range(120):
        # Generate a random loan number with leading zeros
        loan_no = f"LN{str(i+1).zfill(8)}"
        
        # Randomly select first and last names
        first_name = random.choice(first_names)
        last_name = random.choice(kenyan_names)
        
        # Generate random loan amount between 50,000 and 5,000,000
        outstanding_balance = random.uniform(50000, 5000000)
        
        # Generate days in arrears with weighted distribution
        days_in_arrears = random.choices(
            [
                random.randint(0, 30),    # NORMAL
                random.randint(31, 90),   # WATCH
                random.randint(91, 180),  # SUBSTANDARD
                random.randint(181, 360), # DOUBTFUL
                random.randint(361, 720)  # LOSS
            ],
            weights=[50, 20, 15, 10, 5],  # Higher weight for performing loans
            k=1
        )[0]
        
        # Calculate total in arrears (random percentage of outstanding balance)
        if days_in_arrears > 0:
            arrears_percentage = min((days_in_arrears / 30) * 0.05, 0.3)  # Cap at 30% of outstanding balance
            total_in_arrears = outstanding_balance * arrears_percentage
        else:
            total_in_arrears = 0
            
        # Determine classification based on days in arrears
        if days_in_arrears <= 30:
            classification = 'NORMAL'
        elif days_in_arrears <= 90:
            classification = 'WATCH'
        elif days_in_arrears <= 180:
            classification = 'SUBSTANDARD'
        elif days_in_arrears <= 360:
            classification = 'DOUBTFUL'
        else:
            classification = 'LOSS'
            
        loan_record = {
            'Loan_Account_No_': loan_no,
            'Customer_Name': f"{first_name} {last_name}",
            'Outstanding_Balance': round(outstanding_balance, 2),
            'Days_In_Arrears': days_in_arrears,
            'Total_In_Arrears': round(total_in_arrears, 2),
            'Classification': classification
        }
        loan_data.append(loan_record)
    
    # Sort by loan number
    loan_data.sort(key=lambda x: x['Loan_Account_No_'])
        
    return jsonify({'value': loan_data})

@app.route('/user/post-disbursement', methods=['GET'])
def post_disbursement():
    return jsonify({
        'status': 'success',
        'data': {
            'loan_classifications': [
                {
                    'code': 'NORMAL',
                    'name': 'Normal (Performing Loans)',
                    'description': 'Payments are up to date or overdue by less than 30 days',
                    'days_range': '0-30',
                    'provision_rate': 1
                },
                {
                    'code': 'WATCH',
                    'name': 'Watch (Special Mention)',
                    'description': 'Payments are overdue by 31 to 90 days',
                    'days_range': '31-90',
                    'provision_rate': 3
                },
                {
                    'code': 'SUBSTANDARD',
                    'name': 'Substandard',
                    'description': 'Payments are overdue by 91 to 180 days',
                    'days_range': '91-180',
                    'provision_rate': 20
                },
                {
                    'code': 'DOUBTFUL',
                    'name': 'Doubtful',
                    'description': 'Payments are overdue by 181 to 360 days',
                    'days_range': '181-360',
                    'provision_rate': 50
                },
                {
                    'code': 'LOSS',
                    'name': 'Loss (Non-Performing)',
                    'description': 'Payments are overdue by more than 360 days',
                    'days_range': '>360',
                    'provision_rate': 100
                }
            ],
            'sample_loans': MOCK_DATA['navision']['tables'][3]['sample_data']
        }
    })

@app.route('/api/mock/clients/search', methods=['GET'])
def search_clients():
    search_term = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))
    per_page = 10
    
    # Filter clients based on search term
    filtered_clients = [
        client for client in MOCK_CLIENTS
        if search_term in client['name'].lower() or 
           search_term in client['phone'].lower()
    ]
    
    # Calculate pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_clients = filtered_clients[start_idx:end_idx]
    
    return jsonify({
        'clients': paginated_clients,
        'has_more': len(filtered_clients) > end_idx
    })

@app.route('/api/mock/clients/<client_id>/accounts', methods=['GET'])
def get_client_accounts(client_id):
    # Find the client in the mock data
    client = next((c for c in MOCK_CLIENTS if c['id'] == client_id), None)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    # Return the account number(s) for the client
    return jsonify({'accounts': [loan['account_no'] for loan in client['loans']]})

@app.route('/api/correspondence/<client_id>', methods=['GET'])
def get_correspondence(client_id):
    correspondence_type = request.args.get('type', 'all')
    
    if client_id not in MOCK_CORRESPONDENCE:
        return jsonify({
            'items': [],
            'counts': {
                'total': 0,
                'emails': 0,
                'sms': 0,
                'calls': 0
            }
        })
    
    correspondence = MOCK_CORRESPONDENCE[client_id]
    
    # Filter by type if specified
    if correspondence_type != 'all':
        correspondence = [c for c in correspondence if c['type'] == correspondence_type]
    
    # Calculate counts
    counts = {
        'total': len(MOCK_CORRESPONDENCE[client_id]),
        'emails': len([c for c in MOCK_CORRESPONDENCE[client_id] if c['type'] == 'email']),
        'sms': len([c for c in MOCK_CORRESPONDENCE[client_id] if c['type'] == 'sms']),
        'calls': len([c for c in MOCK_CORRESPONDENCE[client_id] if c['type'] == 'call'])
    }
    
    return jsonify({
        'items': correspondence,
        'counts': counts
    })

@app.route('/api/guarantors/<customer_id>', methods=['GET'])
def get_customer_guarantors(customer_id):
    """Get guarantors for a specific customer"""
    client = next((c for c in MOCK_CLIENTS if c['id'] == customer_id), None)
    if not client:
        return jsonify({'error': 'Customer not found'}), 404
    
    return jsonify(client.get('guarantors', []))

@app.route('/api/guarantors/search', methods=['GET'])
def search_guarantors():
    """Search guarantors by name or ID"""
    search_term = request.args.get('q', '').lower()
    
    guarantors = []
    for client in MOCK_CLIENTS:
        for guarantor in client.get('guarantors', []):
            if search_term in guarantor['name'].lower() or search_term in guarantor['id_no'].lower():
                guarantor_data = guarantor.copy()
                guarantor_data['customer_name'] = client['name']
                guarantor_data['customer_id'] = client['id']
                guarantors.append(guarantor_data)
    
    return jsonify(guarantors)

if __name__ == '__main__':
    app.run(port=5003)
