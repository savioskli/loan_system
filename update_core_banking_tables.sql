-- Drop existing tables if they exist
DROP TABLE IF EXISTS core_banking_logs;
DROP TABLE IF EXISTS core_banking_endpoints;
DROP TABLE IF EXISTS core_banking_systems;
DROP TABLE IF EXISTS core_banking_config;

-- Create core_banking_systems table
CREATE TABLE core_banking_systems (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    base_url VARCHAR(255) NOT NULL,
    port INT,
    description TEXT,
    auth_type VARCHAR(20) NOT NULL,
    auth_credentials TEXT,
    headers TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create core_banking_endpoints table
CREATE TABLE core_banking_endpoints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    system_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    path VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    description TEXT,
    parameters TEXT,
    headers TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES core_banking_systems(id) ON DELETE CASCADE
);

-- Create core_banking_logs table
CREATE TABLE core_banking_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    system_id INT NOT NULL,
    endpoint_id INT,
    request_method VARCHAR(10) NOT NULL,
    request_url VARCHAR(255) NOT NULL,
    request_headers TEXT,
    request_body TEXT,
    response_status INT,
    response_headers TEXT,
    response_body TEXT,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES core_banking_systems(id) ON DELETE CASCADE,
    FOREIGN KEY (endpoint_id) REFERENCES core_banking_endpoints(id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX ix_core_banking_systems_is_active ON core_banking_systems(is_active);
CREATE INDEX ix_core_banking_endpoints_is_active ON core_banking_endpoints(is_active);
CREATE INDEX ix_core_banking_endpoints_system_id ON core_banking_endpoints(system_id);
CREATE INDEX ix_core_banking_logs_system_id ON core_banking_logs(system_id);
CREATE INDEX ix_core_banking_logs_endpoint_id ON core_banking_logs(endpoint_id);
CREATE INDEX ix_core_banking_logs_created_at ON core_banking_logs(created_at);
