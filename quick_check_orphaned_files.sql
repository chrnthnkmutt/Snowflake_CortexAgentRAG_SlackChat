-- Quick Check: Find orphaned files that need cleanup
-- Run this query first to see what needs to be cleaned

USE DASH_DB.DASH_SCHEMA;
USE WAREHOUSE DASH_S;

-- Show files in stage vs tables
WITH stage_files AS (
    SELECT relative_path as stage_file
    FROM directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS)
),
table_files AS (
    SELECT DISTINCT relative_path as table_file FROM parse_pdfs
    UNION
    SELECT DISTINCT relative_path as table_file FROM vectorized_pdfs  
    UNION
    SELECT DISTINCT relative_path as table_file FROM parsed_pdfs
)
SELECT 
    'ORPHANED FILES TO CLEANUP:' as status,
    t.table_file as filename
FROM table_files t
LEFT JOIN stage_files s ON t.table_file = s.stage_file  
WHERE s.stage_file IS NULL
ORDER BY t.table_file;

-- If you want to remove a specific file, replace 'YOUR_FILE.pdf' and run:
-- DELETE FROM parse_pdfs WHERE relative_path = 'YOUR_FILE.pdf';
-- DELETE FROM vectorized_pdfs WHERE relative_path = 'YOUR_FILE.pdf';  
-- DELETE FROM parsed_pdfs WHERE relative_path = 'YOUR_FILE.pdf';
