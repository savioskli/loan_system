-- Add backward transitions for the verification workflow

-- First, let's see what workflow definitions we have
SELECT id, name FROM workflow_definitions;

-- Then check existing steps
SELECT id, workflow_id, name, is_start_step FROM workflow_steps ORDER BY workflow_id, step_order;

-- Check existing transitions
SELECT t.id, t.workflow_id, t.from_step_id, fs.name as from_step, t.to_step_id, ts.name as to_step, t.transition_name 
FROM workflow_transitions t
JOIN workflow_steps fs ON t.from_step_id = fs.id
JOIN workflow_steps ts ON t.to_step_id = ts.id
ORDER BY t.workflow_id, t.from_step_id;

-- Add backward transitions for verification declined
-- Note: Replace the step IDs below with the actual IDs from your database

-- Example: Add transition from Verification to Submission (going backward when declined)
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
SELECT 
    t.workflow_id, 
    t.to_step_id, -- The verification step
    t.from_step_id, -- The submission step
    'Decline Verification', 
    NOW()
FROM workflow_transitions t
JOIN workflow_steps fs ON t.from_step_id = fs.id
JOIN workflow_steps ts ON t.to_step_id = ts.id
WHERE fs.name = 'Submission' AND ts.name = 'Verification'
AND NOT EXISTS (
    SELECT 1 FROM workflow_transitions 
    WHERE from_step_id = t.to_step_id AND to_step_id = t.from_step_id
);

-- Example: Add transition from Approval to Verification (going backward when declined)
INSERT INTO workflow_transitions (workflow_id, from_step_id, to_step_id, transition_name, created_at)
SELECT 
    t.workflow_id, 
    t.to_step_id, -- The approval step
    t.from_step_id, -- The verification step
    'Return for Verification', 
    NOW()
FROM workflow_transitions t
JOIN workflow_steps fs ON t.from_step_id = fs.id
JOIN workflow_steps ts ON t.to_step_id = ts.id
WHERE fs.name = 'Verification' AND ts.name = 'Approval'
AND NOT EXISTS (
    SELECT 1 FROM workflow_transitions 
    WHERE from_step_id = t.to_step_id AND to_step_id = t.from_step_id
);
