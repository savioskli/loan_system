# Loan Management System

A comprehensive loan management system built with Flask and MySQL.

## Features

- User Authentication
- Role-based Access Control
- Client Management
- Form Section Management
- Dynamic Module System
- Responsive UI with Tailwind CSS

## Setup

1. Clone the repository
```bash
git clone <repository-url>
cd loan_system
```

2. Create a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the database
```bash
# Create the database
mysql -u root -e "CREATE DATABASE IF NOT EXISTS loan_system;"

# Import the database schema and initial data
mysql -u root loan_system < database/migrations/form_sections.sql
```

4. Configure the application
- Copy `.env.example` to `.env`
- Update the database credentials and other settings in `.env`

5. Run the application
```bash
python app.py
```

The application will be available at http://localhost:5002

## Project Structure

```
loan_system/
├── app.py                 # Application entry point
├── config.py             # Configuration settings
├── extensions.py         # Flask extensions
├── requirements.txt      # Python dependencies
├── database/            
│   └── migrations/       # Database migrations
├── routes/              
│   ├── admin.py         # Admin routes
│   └── auth.py          # Authentication routes
├── services/            
│   └── settings_service.py  # Business logic
├── static/              
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript files
└── templates/           
    ├── admin/           # Admin templates
    ├── auth/            # Authentication templates
    └── base.html        # Base template
```

## Database Schema

### Form Sections Table
```sql
CREATE TABLE form_sections (
  id int NOT NULL AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  module varchar(50) NOT NULL,
  submodule varchar(50) NOT NULL,
  is_active tinyint(1) DEFAULT '1',
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);
```

### Modules Table
```sql
CREATE TABLE modules (
  id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  code varchar(50) NOT NULL,
  description text,
  parent_id int DEFAULT NULL,
  is_active tinyint(1) DEFAULT NULL,
  created_at datetime DEFAULT NULL,
  updated_at datetime DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY code (code),
  KEY parent_id (parent_id),
  CONSTRAINT modules_ibfk_1 FOREIGN KEY (parent_id) REFERENCES modules (id) ON DELETE CASCADE
);
```

## Contributing

1. Create a feature branch
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit
```bash
git add .
git commit -m "Description of your changes"
```

3. Push to your branch
```bash
git push origin feature/your-feature-name
```

4. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
