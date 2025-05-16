-- Create Impact Assessment Verification Workflow

-- Insert workflow definition
INSERT INTO workflow_definitions (name, description, module_id, created_at, updated_at, created_by, is_active)
VALUES (
    'Impact Assessment Verification',
    'Verification process for loan impact claims and evidence',
    28, -- Impact Assessment module ID
    NOW(),
    NOW(),
    1, -- Admin user ID
    1  -- Active
);

-- Get the ID of the newly created workflow
SET @workflow_id = LAST_INSERT_ID();

-- Insert workflow steps

-- Step 1: Initial Submission (Start Step)
INSERT INTO workflow_steps (workflow_id, name, description, step_order, role_id, is_start_step, created_at)
VALUES (
    @workflow_id,
    'Initial Submission',
    'Impact assessment submitted for verification',
    1,
    3, -- Loan Officer role
    1, -- Is start step
    NOW()
);

SET @step1_id = LAST_INSERT_ID();

-- Step 2: Preliminary Review
INSERT INTO workflow_steps (workflow_id, name, description, step_order, role_id, is_start_step, created_at)
VALUES (
    @workflow_id,
    'Preliminary Review',
    'Initial review of impact claims and evidence',
    2,
    8, -- Credit Officer role (assuming they handle verification)
    0, -- Not start step
    NOW()
);

SET @step2_id = LAST_INSERT_ID();

-- Step 3: Evidence Verification
INSERT INTO workflow_steps (workflow_id, name, description, step_order, role_id, is_start_step, created_at)
VALUES (
    @workflow_id,
    'Evidence Verification',
    'Verification of evidence through field visits or documentation',
    3,
    4, -- Collection Officer role (assuming they do field verification)
    0, -- Not start step
    NOW()
);

SET @step3_id = LAST_INSERT_ID();

-- Step 4: Final Approval
INSERT INTO workflow_steps (workflow_id, name, description, step_order, role_id, is_start_step, created_at)
VALUES (
    @workflow_id,
    'Final Approval',
    'Final review and approval of impact claims',
    4,
    2, -- Branch Manager role
    0, -- Not start step
    NOW()
);

SET @step4_id = LAST_INSERT_ID();

-- Step 5: Dispute Resolution
INSERT INTO workflow_steps (workflow_id, name, description, step_order, role_id, is_start_step, created_at)
VALUES (
    @workflow_id,
    'Dispute Resolution',
    'Handle disputed verification decisions',
    5,
    5, -- Collection Supervisor role
    0, -- Not start step
    NOW()
);

SET @step5_id = LAST_INSERT_ID();

-- Insert workflow transitions

-- Initial Submission → Preliminary Review
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
VALUES (@workflow_id, @step1_id, @step2_id, 'Submit for Review', NOW());

-- Preliminary Review → Evidence Verification
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
VALUES (@workflow_id, @step2_id, @step3_id, 'Request Field Verification', NOW());

-- Preliminary Review → Final Approval (Fast-track)
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
VALUES (@workflow_id, @step2_id, @step4_id, 'Fast-track Approval', NOW());

-- Preliminary Review → Initial Submission (Return)
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
VALUES (@workflow_id, @step2_id, @step1_id, 'Return for Revision', NOW());

-- Evidence Verification → Final Approval
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
VALUES (@workflow_id, @step3_id, @step4_id, 'Recommend Approval', NOW());

-- Evidence Verification → Dispute Resolution
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
VALUES (@workflow_id, @step3_id, @step5_id, 'Flag Discrepancy', NOW());

-- Final Approval → Initial Submission (Reject)
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
VALUES (@workflow_id, @step4_id, @step1_id, 'Reject', NOW());

-- Dispute Resolution → Final Approval
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
VALUES (@workflow_id, @step5_id, @step4_id, 'Resolve Dispute', NOW());
