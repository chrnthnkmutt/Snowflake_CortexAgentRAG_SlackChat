# Snowflake RAG System - File Cleanup Tools

This folder contains tools to help you clean up old files from your Snowflake RAG system after removing documents from the `@DASH_PDFS` stage.

## Files in this folder:

### 1. `quick_check_orphaned_files.sql`
**Purpose**: Quick check to identify orphaned files that need cleanup
**Usage**: Run this SQL directly in your Snowflake SQL worksheet

```sql
-- Copy and paste this SQL into your Snowflake worksheet
USE DASH_DB.DASH_SCHEMA;
USE WAREHOUSE DASH_S;
-- The rest of the query will show orphaned files
```

### 2. `cleanup_old_files.sql`
**Purpose**: Comprehensive SQL script for cleaning up old files
**Features**:
- Check current files in stage and tables
- Identify orphaned files
- Remove specific files or all orphaned files
- Refresh the Cortex Search Service

**Usage**:
1. Open your Snowflake SQL worksheet
2. Copy and paste the SQL from this file
3. Run the first few sections to see the current state
4. Uncomment the cleanup sections you want to use
5. Replace `'your_old_filename.pdf'` with actual filenames

### 3. `cleanup_files.py` (in main project directory)
**Purpose**: Interactive Python script for file cleanup
**Features**:
- Interactive menu-driven cleanup
- Connects using your existing JWT authentication
- Real-time feedback and confirmation prompts
- Automatic Cortex Search Service refresh

**Prerequisites**:
```bash
# Make sure you have the required packages
pip install snowflake-snowpark-python python-dotenv
```

**Usage**:
```bash
# From the project root directory
python cleanup_files.py
```

## Typical Workflow:

1. **Remove files from Snowflake stage** (using Snowsight or SQL worksheet):
    ```sql
    REMOVE @DASH_DB.DASH_SCHEMA.DASH_PDFS/old_file.pdf;
    ```

2. **Check for orphaned files**:
    ```bash
    # Option A: Quick SQL check - Run in Snowflake SQL worksheet
    # Copy and paste quick_check_orphaned_files.sql content
    
    # Option B: Interactive Python script (from project root)
    python cleanup_files.py
    ```

3. **Clean up orphaned files**:
    ```bash
    # Option A: Use the SQL script in Snowflake SQL worksheet
    # Copy and paste cleanup_old_files.sql content and run sections
    
    # Option B: Use the interactive Python script (from project root)
    python cleanup_files.py
    ```

4. **Verify cleanup**:
    - Check that files are removed from all tables
    - Verify Cortex Search Service is updated

## Tables that get cleaned:
- `parse_pdfs` - Raw parsed PDF data
- `vectorized_pdfs` - Vectorized content with embeddings
- `parsed_pdfs` - Chunked content for search

## Search Service:
- `VEHICLES_INFO` - Cortex Search Service that gets refreshed after cleanup

## Safety Features:
- All scripts show what will be deleted before acting
- Confirmation prompts for destructive operations
- Commented out dangerous operations by default
- Verification queries to check results

## Configuration:
The Python script automatically uses your existing `.env` configuration:
- Database: `DASH_DB`
- Schema: `DASH_SCHEMA`
- Warehouse: `DASH_S`
- Authentication: JWT using your existing `rsa_key.p8`

## Troubleshooting:

**Connection Issues**:
- Ensure your `.env` file has all required variables
- Check that `rsa_key.p8` exists and is valid
- Verify your conda environment is activated

**Permission Issues**:
- Make sure your user has DELETE permissions on the tables
- Verify your role has access to the Cortex Search Service

**File Not Found**:
- Double-check file names (case sensitive)
- Ensure you're looking at the right stage directory

**⚠️ Important**: SQL scripts must be run in Snowflake SQL worksheets. Do not attempt to run `.sql` files in other environments.
