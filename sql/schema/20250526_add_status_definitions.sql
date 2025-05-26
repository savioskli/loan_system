-- Add status definitions
BEGIN;

-- Insert status values for various system entities
INSERT INTO system_reference_values (field_id, value, label, is_active) VALUES
-- Loan Status
(4, 'PENDING_APPROVAL', 'Pending Approval', 1),
(4, 'APPROVED', 'Approved', 1),
(4, 'REJECTED', 'Rejected', 1),
(4, 'DISBURSED', 'Disbursed', 1),
(4, 'ACTIVE', 'Active', 1),
(4, 'CLOSED', 'Closed', 1),
(4, 'DEFAULTED', 'Defaulted', 1),
(4, 'WRITTEN_OFF', 'Written Off', 1),
(4, 'RESTRUCTURED', 'Restructured', 1),

-- Client Status
(4, 'CLIENT_ACTIVE', 'Active Client', 1),
(4, 'CLIENT_INACTIVE', 'Inactive Client', 1),
(4, 'CLIENT_BLACKLISTED', 'Blacklisted Client', 1),
(4, 'CLIENT_DECEASED', 'Deceased Client', 1),

-- Collateral Status
(4, 'COLLATERAL_PENDING', 'Pending Verification', 1),
(4, 'COLLATERAL_VERIFIED', 'Verified', 1),
(4, 'COLLATERAL_REJECTED', 'Rejected', 1),
(4, 'COLLATERAL_RELEASED', 'Released', 1),
(4, 'COLLATERAL_SEIZED', 'Seized', 1),

-- Payment Status
(4, 'PAYMENT_PENDING', 'Payment Pending', 1),
(4, 'PAYMENT_SUCCESSFUL', 'Payment Successful', 1),
(4, 'PAYMENT_FAILED', 'Payment Failed', 1),
(4, 'PAYMENT_REVERSED', 'Payment Reversed', 1),

-- Document Status
(4, 'DOCUMENT_PENDING', 'Document Pending', 1),
(4, 'DOCUMENT_VERIFIED', 'Document Verified', 1),
(4, 'DOCUMENT_REJECTED', 'Document Rejected', 1),
(4, 'DOCUMENT_EXPIRED', 'Document Expired', 1),

-- Guarantor Status
(4, 'GUARANTOR_PENDING', 'Pending Approval', 1),
(4, 'GUARANTOR_APPROVED', 'Approved', 1),
(4, 'GUARANTOR_REJECTED', 'Rejected', 1),
(4, 'GUARANTOR_WITHDRAWN', 'Withdrawn', 1),

-- Collection Status
(4, 'COLLECTION_PENDING', 'Collection Pending', 1),
(4, 'COLLECTION_IN_PROGRESS', 'Collection In Progress', 1),
(4, 'COLLECTION_SUCCESSFUL', 'Collection Successful', 1),
(4, 'COLLECTION_FAILED', 'Collection Failed', 1),

-- Legal Case Status
(4, 'LEGAL_PENDING', 'Legal Case Pending', 1),
(4, 'LEGAL_IN_PROGRESS', 'Legal Case In Progress', 1),
(4, 'LEGAL_RESOLVED', 'Legal Case Resolved', 1),
(4, 'LEGAL_WITHDRAWN', 'Legal Case Withdrawn', 1),

-- Account Status
(4, 'ACCOUNT_ACTIVE', 'Account Active', 1),
(4, 'ACCOUNT_INACTIVE', 'Account Inactive', 1),
(4, 'ACCOUNT_SUSPENDED', 'Account Suspended', 1),
(4, 'ACCOUNT_CLOSED', 'Account Closed', 1),

-- Staff Status
(4, 'STAFF_ACTIVE', 'Staff Active', 1),
(4, 'STAFF_INACTIVE', 'Staff Inactive', 1),
(4, 'STAFF_ON_LEAVE', 'Staff On Leave', 1),
(4, 'STAFF_SUSPENDED', 'Staff Suspended', 1),
(4, 'STAFF_TERMINATED', 'Staff Terminated', 1);

COMMIT;
