BEGIN;

CREATE TABLE form_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    user_id INT NOT NULL,
    organization_id INT NOT NULL,
    form_data JSON NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, approved, rejected
    created_by INT NOT NULL,
    updated_by INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

-- Add indexes for better performance
CREATE INDEX idx_form_submissions_module ON form_submissions(module_id);
CREATE INDEX idx_form_submissions_user ON form_submissions(user_id);
CREATE INDEX idx_form_submissions_org ON form_submissions(organization_id);
CREATE INDEX idx_form_submissions_status ON form_submissions(status);

COMMIT;
