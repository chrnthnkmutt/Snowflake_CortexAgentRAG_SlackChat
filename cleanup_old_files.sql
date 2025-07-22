-- =====================================================
-- CLEANUP SCRIPT: Remove Old Files from RAG System
-- =====================================================
-- This script removes old document data from all tables and services
-- after you've deleted files from the @DASH_PDFS stage

USE DASH_DB.DASH_SCHEMA;
USE WAREHOUSE DASH_S;

-- =====================================================
-- STEP 1: Check what files currently exist in the stage
-- =====================================================
SELECT 'Files currently in stage:' as info;
SELECT relative_path, size, last_modified 
FROM directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS)
ORDER BY last_modified DESC;

-- =====================================================
-- STEP 2: Check what files are in the vectorized tables
-- =====================================================
SELECT 'Files in parse_pdfs table:' as info;
SELECT DISTINCT relative_path FROM parse_pdfs ORDER BY relative_path;

SELECT 'Files in vectorized_pdfs table:' as info;
SELECT DISTINCT relative_path, title FROM vectorized_pdfs ORDER BY relative_path;

SELECT 'Files in parsed_pdfs table:' as info;
SELECT DISTINCT relative_path, title FROM parsed_pdfs ORDER BY relative_path;

-- =====================================================
-- STEP 3: Identify orphaned files (in tables but not in stage)
-- =====================================================
SELECT 'Orphaned files that need cleanup:' as info;

-- Files in parse_pdfs but not in stage
SELECT 'In parse_pdfs but not in stage:' as table_name, p.relative_path
FROM parse_pdfs p
LEFT JOIN directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS) d ON p.relative_path = d.relative_path
WHERE d.relative_path IS NULL

UNION ALL

-- Files in vectorized_pdfs but not in stage  
SELECT 'In vectorized_pdfs but not in stage:' as table_name, v.relative_path
FROM vectorized_pdfs v
LEFT JOIN directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS) d ON v.relative_path = d.relative_path
WHERE d.relative_path IS NULL

UNION ALL

-- Files in parsed_pdfs but not in stage
SELECT 'In parsed_pdfs but not in stage:' as table_name, p.relative_path
FROM parsed_pdfs p
LEFT JOIN directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS) d ON p.relative_path = d.relative_path
WHERE d.relative_path IS NULL;

-- =====================================================
-- STEP 4: Remove specific file (REPLACE 'filename.pdf' with your file)
-- =====================================================
-- ⚠️  REPLACE 'your_old_filename.pdf' with the actual filename you want to remove
-- ⚠️  Uncomment the DELETE statements below after confirming the file name

/*
SET old_file_name = 'your_old_filename.pdf';  -- CHANGE THIS TO YOUR FILE NAME

-- Remove from parse_pdfs
DELETE FROM parse_pdfs WHERE relative_path = $old_file_name;

-- Remove from vectorized_pdfs  
DELETE FROM vectorized_pdfs WHERE relative_path = $old_file_name;

-- Remove from parsed_pdfs
DELETE FROM parsed_pdfs WHERE relative_path = $old_file_name;

-- Verify deletion
SELECT 'Verification - file should not appear in these results:' as info;
SELECT 'parse_pdfs' as table_name, COUNT(*) as remaining_records FROM parse_pdfs WHERE relative_path = $old_file_name
UNION ALL
SELECT 'vectorized_pdfs' as table_name, COUNT(*) as remaining_records FROM vectorized_pdfs WHERE relative_path = $old_file_name  
UNION ALL
SELECT 'parsed_pdfs' as table_name, COUNT(*) as remaining_records FROM parsed_pdfs WHERE relative_path = $old_file_name;
*/

-- =====================================================
-- STEP 5: Clean up ALL orphaned files automatically
-- =====================================================
-- This removes all files that exist in tables but not in the stage
-- ⚠️  Only run this if you want to clean ALL orphaned files

/*
-- Remove orphaned files from parse_pdfs
DELETE FROM parse_pdfs 
WHERE relative_path NOT IN (
    SELECT relative_path FROM directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS)
);

-- Remove orphaned files from vectorized_pdfs
DELETE FROM vectorized_pdfs 
WHERE relative_path NOT IN (
    SELECT relative_path FROM directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS)
);

-- Remove orphaned files from parsed_pdfs
DELETE FROM parsed_pdfs 
WHERE relative_path NOT IN (
    SELECT relative_path FROM directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS)
);

-- Show cleanup summary
SELECT 'Cleanup completed. Current file counts:' as info;
SELECT 'parse_pdfs' as table_name, COUNT(DISTINCT relative_path) as file_count FROM parse_pdfs
UNION ALL
SELECT 'vectorized_pdfs' as table_name, COUNT(DISTINCT relative_path) as file_count FROM vectorized_pdfs
UNION ALL  
SELECT 'parsed_pdfs' as table_name, COUNT(DISTINCT relative_path) as file_count FROM parsed_pdfs
UNION ALL
SELECT 'stage_files' as table_name, COUNT(*) as file_count FROM directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS);
*/

-- =====================================================
-- STEP 6: Refresh the Cortex Search Service
-- =====================================================
-- After cleaning up the tables, refresh the search service to remove old data
-- ⚠️  Uncomment this after running the cleanup

/*
-- Recreate the Cortex Search Service to remove old indexed data
DROP CORTEX SEARCH SERVICE IF EXISTS DASH_DB.DASH_SCHEMA.VEHICLES_INFO;

create or replace CORTEX SEARCH SERVICE DASH_DB.DASH_SCHEMA.VEHICLES_INFO
ON PAGE_CONTENT
WAREHOUSE = DASH_S
TARGET_LAG = '1 hour'
AS (
    SELECT '' AS PAGE_URL, PAGE_CONTENT, TITLE, RELATIVE_PATH
    FROM parsed_pdfs
);

SELECT 'Cortex Search Service recreated successfully!' as info;
*/
