USE DASH_DB.DASH_SCHEMA;
USE WAREHOUSE DASH_S;

create or replace table parse_pdfs as 
select relative_path, SNOWFLAKE.CORTEX.PARSE_DOCUMENT(@DASH_DB.DASH_SCHEMA.DASH_PDFS,relative_path,{'mode':'LAYOUT'}) as data
    from directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS);

-- Create a table for vectorized content from parsed PDFs
create or replace table vectorized_pdfs as
    select 
        relative_path, 
        REGEXP_REPLACE(relative_path, '\\.pdf$', '') as title,
        TO_VARIANT(data):content as OBJECT,
        SNOWFLAKE.CORTEX.EMBED_TEXT_1024('voyage-multilingual-2', TO_VARIANT(data):content) as EMBED
    from parse_pdfs where TO_VARIANT(data):content is not null;

create or replace table parsed_pdfs as (
    with tmp_parsed as (select
        relative_path,
        SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER(TO_VARIANT(data):content, 'MARKDOWN', 1800, 300) AS chunks
        -- Chunks of 1800 characters with 300 character overlap
    from parse_pdfs where TO_VARIANT(data):content is not null)
    select
        TO_VARCHAR(c.value) as PAGE_CONTENT,
        REGEXP_REPLACE(relative_path, '\\.pdf$', '') as TITLE,
        'DASH_DB.DASH_SCHEMA.DASH_PDFS' as INPUT_STAGE,
        RELATIVE_PATH as RELATIVE_PATH
    from tmp_parsed p, lateral FLATTEN(INPUT => p.chunks) c
);

-- Cortex Search Service uses arctic-embed-m-v1.5 as the default embedding model
-- This model typically has 768 dimensions
create or replace CORTEX SEARCH SERVICE DASH_DB.DASH_SCHEMA.VEHICLES_INFO
ON PAGE_CONTENT
WAREHOUSE = DASH_S
TARGET_LAG = '1 hour'
AS (
    SELECT '' AS PAGE_URL, PAGE_CONTENT, TITLE, RELATIVE_PATH
    FROM parsed_pdfs
);