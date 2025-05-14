-- Add Impact Assessment module to post_disbursement_modules table
-- First, find the Post Disbursement parent module ID
SET @post_disbursement_id = (SELECT id FROM post_disbursement_modules WHERE name = 'Post Disbursement' AND parent_id IS NULL LIMIT 1);

-- If Post Disbursement parent module doesn't exist, create it
INSERT INTO post_disbursement_modules (name, description, url, parent_id, created_at, hidden, `order`)
SELECT 'Post Disbursement', 'Post Disbursement Activities', '#', NULL, NOW(), 0, 1
WHERE @post_disbursement_id IS NULL;

-- Get the Post Disbursement parent ID again if we just created it
SET @post_disbursement_id = COALESCE(@post_disbursement_id, LAST_INSERT_ID());

-- Check if Impact Assessment module already exists
SET @impact_assessment_exists = (SELECT COUNT(*) FROM post_disbursement_modules WHERE name = 'Impact Assessment' AND parent_id = @post_disbursement_id);

-- Add Impact Assessment module if it doesn't exist
INSERT INTO post_disbursement_modules (name, description, url, parent_id, created_at, hidden, `order`)
SELECT 'Impact Assessment', 'Track and verify loan impact', '/user/impact_assessment', 
@post_disbursement_id, NOW(), 0, (SELECT COALESCE(MAX(`order`), 0) + 1 FROM post_disbursement_modules WHERE parent_id = @post_disbursement_id)
WHERE @impact_assessment_exists = 0;
