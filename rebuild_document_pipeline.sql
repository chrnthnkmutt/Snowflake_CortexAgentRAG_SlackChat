-- =====================================================
-- REBUILD DOCUMENT PROCESSING PIPELINE
-- =====================================================
-- This script will reprocess all PDF files in the stage
-- and rebuild the vectorized tables and search service

USE DASH_DB.DASH_SCHEMA;
USE WAREHOUSE DASH_S;

-- =====================================================
-- STEP 1: Check current files in stage
-- =====================================================
SELECT 'Current files in stage:' as info;
SELECT relative_path, size, last_modified 
FROM directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS)
ORDER BY relative_path;

-- =====================================================
-- STEP 2: Parse PDF documents from stage
-- =====================================================
SELECT 'Step 2: Parsing PDF documents...' as info;

CREATE OR REPLACE TABLE parse_pdfs AS 
SELECT 
    relative_path, 
    SNOWFLAKE.CORTEX.PARSE_DOCUMENT(@DASH_DB.DASH_SCHEMA.DASH_PDFS, relative_path, {'mode':'LAYOUT'}) as data
FROM directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS)
WHERE LOWER(relative_path) LIKE '%.pdf';

-- Check parsing results
SELECT 'Parsing results:' as info;
SELECT 
    relative_path,
    CASE 
        WHEN data IS NOT NULL THEN '✅ Parsed successfully'
        ELSE '❌ Parsing failed'
    END as status,
    LENGTH(TO_VARIANT(data):content) as content_length
FROM parse_pdfs
ORDER BY relative_path;

-- =====================================================
-- STEP 3: Create vectorized content for similarity search
-- =====================================================
SELECT 'Step 3: Creating vectorized content...' as info;

CREATE OR REPLACE TABLE vectorized_pdfs AS
SELECT 
    relative_path, 
    REGEXP_REPLACE(relative_path, '\\.pdf$', '') as title,
    TO_VARIANT(data):content as OBJECT,
    SNOWFLAKE.CORTEX.EMBED_TEXT_1024('voyage-multilingual-2', TO_VARIANT(data):content) as EMBED
FROM parse_pdfs 
WHERE TO_VARIANT(data):content IS NOT NULL
  AND LENGTH(TO_VARIANT(data):content) > 50; -- Only process files with meaningful content

-- Check vectorization results
SELECT 'Vectorization results:' as info;
SELECT 
    relative_path,
    title,
    LENGTH(OBJECT) as content_length,
    ARRAY_SIZE(EMBED) as embedding_dimensions
FROM vectorized_pdfs
ORDER BY relative_path;

-- =====================================================
-- STEP 4: Create chunked content for Cortex Search
-- =====================================================
SELECT 'Step 4: Creating chunked content...' as info;

CREATE OR REPLACE TABLE parsed_pdfs AS (
    WITH tmp_parsed AS (
        SELECT
            relative_path,
            SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER(
                TO_VARIANT(data):content, 
                'MARKDOWN', 
                1800,  -- Chunk size
                300    -- Overlap
            ) AS chunks
        FROM parse_pdfs 
        WHERE TO_VARIANT(data):content IS NOT NULL
          AND LENGTH(TO_VARIANT(data):content) > 50
    )
    SELECT
        TO_VARCHAR(c.value) as PAGE_CONTENT,
        REGEXP_REPLACE(relative_path, '\\.pdf$', '') as TITLE,
        'DASH_DB.DASH_SCHEMA.DASH_PDFS' as INPUT_STAGE,
        RELATIVE_PATH as RELATIVE_PATH
    FROM tmp_parsed p, 
    LATERAL FLATTEN(INPUT => p.chunks) c
    WHERE LENGTH(TO_VARCHAR(c.value)) > 100  -- Only keep meaningful chunks
);

-- Check chunking results
SELECT 'Chunking results:' as info;
SELECT 
    relative_path,
    title,
    COUNT(*) as chunk_count,
    AVG(LENGTH(page_content)) as avg_chunk_length
FROM parsed_pdfs
GROUP BY relative_path, title
ORDER BY relative_path;

-- =====================================================
-- STEP 5: Create/Recreate Cortex Search Service
-- =====================================================
SELECT 'Step 5: Creating Cortex Search Service...' as info;

-- Drop existing service if it exists
DROP CORTEX SEARCH SERVICE IF EXISTS DASH_DB.DASH_SCHEMA.VEHICLES_INFO;

-- Create new search service
CREATE OR REPLACE CORTEX SEARCH SERVICE DASH_DB.DASH_SCHEMA.VEHICLES_INFO
ON PAGE_CONTENT
WAREHOUSE = DASH_S
TARGET_LAG = '1 hour'
AS (
    SELECT 
        '' AS PAGE_URL, 
        PAGE_CONTENT, 
        TITLE, 
        RELATIVE_PATH
    FROM parsed_pdfs
);

-- =====================================================
-- STEP 6: Final verification
-- =====================================================
SELECT 'Final verification:' as info;

SELECT 'Table record counts:' as summary;
SELECT 'parse_pdfs' as table_name, COUNT(*) as record_count FROM parse_pdfs
UNION ALL
SELECT 'vectorized_pdfs' as table_name, COUNT(*) as record_count FROM vectorized_pdfs
UNION ALL  
SELECT 'parsed_pdfs' as table_name, COUNT(*) as record_count FROM parsed_pdfs;

SELECT 'Files processed successfully:' as summary;
SELECT DISTINCT relative_path as processed_files FROM parsed_pdfs ORDER BY relative_path;

SELECT '✅ Document processing pipeline rebuilt successfully!' as status;
SELECT 'You can now test the Cortex Agents API again.' as next_step;
