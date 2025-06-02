BEGIN;

CREATE TABLE form_drafts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    organization_id INT NOT NULL,
    module_id INT NOT NULL,
    section_id INT NOT NULL,
    form_data JSON NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (section_id) REFERENCES form_sections(id)
);

-- Add indexes for better performance
CREATE INDEX idx_form_drafts_user ON form_drafts(user_id);
CREATE INDEX idx_form_drafts_org ON form_drafts(organization_id);
CREATE INDEX idx_form_drafts_module ON form_drafts(module_id);
CREATE INDEX idx_form_drafts_section ON form_drafts(section_id);

COMMIT;
