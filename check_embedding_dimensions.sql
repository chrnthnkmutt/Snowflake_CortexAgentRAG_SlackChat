-- SQL queries to find the exact vector embedding dimensions for Cortex Search Service
-- Run these queries in your Snowflake environment to discover embedding details

-- 1. Check Cortex Search Service metadata and configuration
SELECT 
    service_name,
    service_schema,
    definition,
    target_lag,
    warehouse,
    comment
FROM INFORMATION_SCHEMA.CORTEX_SEARCH_SERVICES 
WHERE service_name = 'VEHICLES_INFO' 
    AND service_schema = 'DASH_SCHEMA';

-- 2. Alternative query using SHOW command for Cortex Search Services
SHOW CORTEX SEARCH SERVICES IN SCHEMA DASH_DB.DASH_SCHEMA;

-- 3. Check the service definition and search for embedding model details
DESCRIBE CORTEX SEARCH SERVICE DASH_DB.DASH_SCHEMA.VEHICLES_INFO;

-- If above don't work, try this simpler approach
SELECT 
    'VEHICLES_INFO' as service_name,
    CURRENT_TIMESTAMP() as check_time;

-- 5. Check for any embedding-related metadata in system tables
SELECT 
    table_name,
    column_name,
    data_type,
    comment
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE table_schema = 'DASH_SCHEMA' 
    AND table_name LIKE '%EMBEDDING%' 
    OR comment LIKE '%embedding%' 
    OR comment LIKE '%vector%';

-- 6. Test the embedding function to see output dimensions
-- This will show you the actual embedding vector and you can count dimensions
SELECT 
    SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', 'test text') as embedding_768,
    768 as dimensions_768;

SELECT 
    SNOWFLAKE.CORTEX.EMBED_TEXT_1024('e5-large-v2', 'test text') as embedding_1024,
    1024 as dimensions_1024;

-- 7. Check what embedding models are available in your Snowflake account
-- This will help identify which model Cortex Search might be using
SELECT 
    SNOWFLAKE.CORTEX.EMBED_TEXT_768('multilingual-e5-large', 'test') as test_multilingual,
    768 as multilingual_dims;

-- 8. Query the parsed_pdfs table to see if there are any embedding columns
DESCRIBE TABLE DASH_DB.DASH_SCHEMA.parsed_pdfs;

-- 9. Search for any tables that might contain embedding vectors
SELECT 
    table_catalog,
    table_schema,
    table_name,
    column_name,
    data_type
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE (column_name LIKE '%EMBED%' 
    OR column_name LIKE '%VECTOR%' 
    OR data_type LIKE '%ARRAY%')
    AND table_schema = 'DASH_SCHEMA';

-- 10. Check if there are any system views with embedding information
SELECT 
    *
FROM INFORMATION_SCHEMA.VIEWS 
WHERE view_name LIKE '%CORTEX%' 
    OR view_name LIKE '%EMBEDDING%' 
    OR view_name LIKE '%VECTOR%';

-- 11. Try to get more details about the search service configuration
-- This might reveal the underlying embedding model
SELECT 
    GET_DDL('CORTEX_SEARCH_SERVICE', 'DASH_DB.DASH_SCHEMA.VEHICLES_INFO') as service_ddl;

-- 12. Check account parameters for Cortex settings
SHOW PARAMETERS LIKE '%CORTEX%' IN ACCOUNT;

-- 13. Query to check the search service status and any internal metadata
SELECT 
    SYSTEM$CORTEX_SEARCH_PREVIEW('DASH_DB.DASH_SCHEMA.VEHICLES_INFO', 'test query', {}) as search_preview;

-- Additional notes:
-- If the above queries don't reveal the exact dimensions, you can:
-- 1. Contact Snowflake support for the specific embedding model used
-- 2. Check Snowflake documentation for your version
-- 3. The most common dimensions for Cortex Search are:
--    - 768 dimensions (e5-base-v2)
--    - 1024 dimensions (e5-large-v2) 
--    - 1536 dimensions (similar to OpenAI models)
