-- SQL script to add form sections and fields for Corporate Client Management
-- Created: 2025-06-20

-- First, let's create the necessary form sections for corporate client management

-- 1. Officials Section
INSERT INTO form_sections (module_id, name, description, `order`, is_active)
VALUES (33, 'Officials', 'Information about corporate officials such as directors and executives', 10, 1);

-- 2. Signatories Section
INSERT INTO form_sections (module_id, name, description, `order`, is_active)
VALUES (33, 'Signatories', 'Authorized signatories for the corporate client', 20, 1);

-- 3. Attachments Section
INSERT INTO form_sections (module_id, name, description, `order`, is_active)
VALUES (33, 'Corporate Documents', 'Required corporate documentation and attachments', 30, 1);

-- 4. Services Section
INSERT INTO form_sections (module_id, name, description, `order`, is_active)
VALUES (33, 'Services', 'Products and services subscribed by the corporate client', 40, 1);

-- Now let's add fields for each section
-- Get the section IDs first (we'll use variables in the actual SQL)
SET @officials_section_id = (SELECT id FROM form_sections WHERE module_id = 33 AND name = 'Officials');
SET @signatories_section_id = (SELECT id FROM form_sections WHERE module_id = 33 AND name = 'Signatories');
SET @documents_section_id = (SELECT id FROM form_sections WHERE module_id = 33 AND name = 'Corporate Documents');
SET @services_section_id = (SELECT id FROM form_sections WHERE module_id = 33 AND name = 'Services');

-- Fields for Officials section
INSERT INTO form_fields (module_id, section_id, field_name, field_label, field_placeholder, field_type, is_required, field_order, organization_id)
VALUES 
(33, @officials_section_id, 'official_name', 'Full Name', 'Enter official\'s full name', 'text', 1, 1, 1),
(33, @officials_section_id, 'official_position', 'Position', 'Enter position/title', 'text', 1, 2, 1),
(33, @officials_section_id, 'official_id_number', 'ID Number', 'Enter national ID number', 'text', 1, 3, 1),
(33, @officials_section_id, 'official_contact', 'Contact Number', 'Enter phone number', 'tel', 1, 4, 1),
(33, @officials_section_id, 'official_email', 'Email Address', 'Enter email address', 'email', 0, 5, 1);

-- Fields for Signatories section
INSERT INTO form_fields (module_id, section_id, field_name, field_label, field_placeholder, field_type, is_required, field_order, organization_id)
VALUES 
(33, @signatories_section_id, 'signatory_name', 'Full Name', 'Enter signatory\'s full name', 'text', 1, 1, 1),
(33, @signatories_section_id, 'signatory_position', 'Position', 'Enter position/title', 'text', 1, 2, 1),
(33, @signatories_section_id, 'signatory_id_number', 'ID Number', 'Enter national ID number', 'text', 1, 3, 1),
(33, @signatories_section_id, 'signatory_level', 'Signature Level', 'Enter signature level (e.g., A, B, C)', 'select', 1, 4, 1);

-- Add options for signature level
UPDATE form_fields 
SET options = '[{"value":"A","label":"Level A"},{"value":"B","label":"Level B"},{"value":"C","label":"Level C"}]'
WHERE module_id = 33 AND field_name = 'signatory_level';

-- Fields for Corporate Documents section
INSERT INTO form_fields (module_id, section_id, field_name, field_label, field_placeholder, field_type, is_required, field_order, organization_id)
VALUES 
(33, @documents_section_id, 'document_type', 'Document Type', 'Select document type', 'select', 1, 1, 1),
(33, @documents_section_id, 'document_file', 'Upload Document', 'Select file to upload', 'file', 1, 2, 1),
(33, @documents_section_id, 'document_description', 'Description', 'Enter brief description', 'textarea', 0, 3, 1);

-- Add options for document type
UPDATE form_fields 
SET options = '[
  {"value":"certificate_of_incorporation","label":"Certificate of Incorporation"},
  {"value":"business_license","label":"Business License"},
  {"value":"tax_compliance","label":"Tax Compliance Certificate"},
  {"value":"cr12","label":"CR12 Form"},
  {"value":"articles_of_association","label":"Articles of Association"},
  {"value":"board_resolution","label":"Board Resolution"},
  {"value":"financial_statements","label":"Financial Statements"}
]'
WHERE module_id = 33 AND field_name = 'document_type';

-- Fields for Services section
INSERT INTO form_fields (module_id, section_id, field_name, field_label, field_placeholder, field_type, is_required, field_order, organization_id)
VALUES 
(33, @services_section_id, 'service_type', 'Service Type', 'Select service type', 'select', 1, 1, 1),
(33, @services_section_id, 'service_details', 'Service Details', 'Enter service details', 'textarea', 1, 2, 1),
(33, @services_section_id, 'service_start_date', 'Start Date', 'Select start date', 'date', 1, 3, 1),
(33, @services_section_id, 'service_end_date', 'End Date', 'Select end date', 'date', 0, 4, 1);

-- Add client type restrictions to make these sections visible only for corporate clients
UPDATE form_sections
SET client_type_restrictions = '[2]'  -- Assuming 2 is the ID for corporate clients
WHERE name IN ('Officials', 'Signatories', 'Corporate Documents') AND module_id = 33;
