-- Core Banking Tables Configuration
CREATE TABLE IF NOT EXISTS core_banking_tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    system_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_table_mapping (system_type, table_name)
);
