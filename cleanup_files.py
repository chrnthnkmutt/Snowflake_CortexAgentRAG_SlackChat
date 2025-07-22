#!/usr/bin/env python3
"""
Interactive File Cleanup Tool for Snowflake RAG System
This script helps you remove old document data from the vectorized tables
after deleting files from the Snowflake stage.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from snowflake.snowpark import Session
from snowflake.snowpark import functions as F

load_dotenv()

# Configuration
ACCOUNT = os.getenv("ACCOUNT")
HOST = os.getenv("HOST")
USER = os.getenv("DEMO_USER")
DATABASE = os.getenv("DEMO_DATABASE", "DASH_DB")
SCHEMA = os.getenv("DEMO_SCHEMA", "DASH_SCHEMA")
ROLE = os.getenv("DEMO_USER_ROLE")
WAREHOUSE = os.getenv("WAREHOUSE", "DASH_S")
RSA_PRIVATE_KEY_PATH = os.getenv("RSA_PRIVATE_KEY_PATH")

def init_session():
    """Initialize Snowflake session."""
    connection_parameters = {
        "user": USER,
        "authenticator": "SNOWFLAKE_JWT",
        "private_key_file": RSA_PRIVATE_KEY_PATH,
        "account": ACCOUNT,
        "warehouse": WAREHOUSE,
        "database": DATABASE,
        "schema": SCHEMA,
        "role": ROLE,
        "host": HOST
    }
    
    return Session.builder.configs(connection_parameters).create()

def check_stage_files(session):
    """Check what files currently exist in the stage."""
    print("📁 Files currently in @DASH_PDFS stage:")
    try:
        stage_files_sql = """
        SELECT relative_path, size, last_modified 
        FROM directory(@DASH_DB.DASH_SCHEMA.DASH_PDFS)
        ORDER BY last_modified DESC
        """
        stage_files = session.sql(stage_files_sql).collect()
        
        if stage_files:
            for file in stage_files:
                print(f"   ✅ {file['RELATIVE_PATH']} (Size: {file['SIZE']}, Modified: {file['LAST_MODIFIED']})")
            return [file['RELATIVE_PATH'] for file in stage_files]
        else:
            print("   ❌ No files found in stage")
            return []
    except Exception as e:
        print(f"   ❌ Error checking stage: {e}")
        return []

def check_table_files(session):
    """Check what files exist in the vectorized tables."""
    tables = ['parse_pdfs', 'vectorized_pdfs', 'parsed_pdfs']
    table_files = {}
    
    for table in tables:
        print(f"\n📊 Files in {table} table:")
        try:
            files_sql = f"SELECT DISTINCT relative_path FROM {table} ORDER BY relative_path"
            files = session.sql(files_sql).collect()
            
            if files:
                file_list = [file['RELATIVE_PATH'] for file in files]
                table_files[table] = file_list
                for file in file_list:
                    print(f"   📄 {file}")
            else:
                print(f"   ❌ No files found in {table}")
                table_files[table] = []
        except Exception as e:
            print(f"   ❌ Error checking {table}: {e}")
            table_files[table] = []
    
    return table_files

def find_orphaned_files(stage_files, table_files):
    """Find files that exist in tables but not in stage."""
    all_table_files = set()
    for table, files in table_files.items():
        all_table_files.update(files)
    
    stage_files_set = set(stage_files)
    orphaned_files = all_table_files - stage_files_set
    
    return list(orphaned_files)

def remove_file_from_tables(session, filename):
    """Remove a specific file from all vectorized tables."""
    tables = ['parse_pdfs', 'vectorized_pdfs', 'parsed_pdfs']
    removed_counts = {}
    
    print(f"\n🗑️  Removing '{filename}' from all tables...")
    
    for table in tables:
        try:
            # First check how many records will be affected
            count_sql = f"SELECT COUNT(*) as count FROM {table} WHERE relative_path = '{filename}'"
            count_result = session.sql(count_sql).collect()
            record_count = count_result[0]['COUNT'] if count_result else 0
            
            if record_count > 0:
                # Delete the records
                delete_sql = f"DELETE FROM {table} WHERE relative_path = '{filename}'"
                session.sql(delete_sql).collect()
                removed_counts[table] = record_count
                print(f"   ✅ Removed {record_count} records from {table}")
            else:
                print(f"   ℹ️  No records found in {table}")
                removed_counts[table] = 0
                
        except Exception as e:
            print(f"   ❌ Error removing from {table}: {e}")
            removed_counts[table] = 0
    
    return removed_counts

def refresh_cortex_search_service(session):
    """Refresh the Cortex Search Service to remove old indexed data."""
    print("\n🔄 Refreshing Cortex Search Service...")
    
    try:
        # Drop existing service
        session.sql("DROP CORTEX SEARCH SERVICE IF EXISTS DASH_DB.DASH_SCHEMA.VEHICLES_INFO").collect()
        print("   ✅ Dropped existing Cortex Search Service")
        
        # Recreate service
        create_service_sql = """
        CREATE OR REPLACE CORTEX SEARCH SERVICE DASH_DB.DASH_SCHEMA.VEHICLES_INFO
        ON PAGE_CONTENT
        WAREHOUSE = DASH_S
        TARGET_LAG = '1 hour'
        AS (
            SELECT '' AS PAGE_URL, PAGE_CONTENT, TITLE, RELATIVE_PATH
            FROM parsed_pdfs
        )
        """
        session.sql(create_service_sql).collect()
        print("   ✅ Recreated Cortex Search Service successfully")
        
    except Exception as e:
        print(f"   ❌ Error refreshing Cortex Search Service: {e}")

def main():
    print("🧹 Snowflake RAG System - File Cleanup Tool")
    print("=" * 50)
    
    try:
        # Initialize session
        print("🔗 Connecting to Snowflake...")
        session = init_session()
        session.use_role("SYSADMIN")
        print("   ✅ Connected successfully")
        
        # Check current state
        stage_files = check_stage_files(session)
        table_files = check_table_files(session)
        
        # Find orphaned files
        orphaned_files = find_orphaned_files(stage_files, table_files)
        
        if not orphaned_files:
            print("\n✅ No orphaned files found! All table data matches stage files.")
            return
        
        print(f"\n⚠️  Found {len(orphaned_files)} orphaned file(s):")
        for i, file in enumerate(orphaned_files, 1):
            print(f"   {i}. {file}")
        
        # Ask user what to do
        print("\nChoose an option:")
        print("1. Remove a specific file")
        print("2. Remove ALL orphaned files")
        print("3. Exit without changes")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Remove specific file
            print("\nSelect file to remove:")
            for i, file in enumerate(orphaned_files, 1):
                print(f"   {i}. {file}")
            
            try:
                file_choice = int(input(f"\nEnter file number (1-{len(orphaned_files)}): ")) - 1
                if 0 <= file_choice < len(orphaned_files):
                    selected_file = orphaned_files[file_choice]
                    
                    confirm = input(f"\n⚠️  Are you sure you want to remove '{selected_file}'? (yes/no): ")
                    if confirm.lower() in ['yes', 'y']:
                        removed_counts = remove_file_from_tables(session, selected_file)
                        total_removed = sum(removed_counts.values())
                        
                        if total_removed > 0:
                            print(f"\n✅ Successfully removed '{selected_file}' ({total_removed} total records)")
                            
                            refresh_choice = input("\n🔄 Refresh Cortex Search Service? (recommended) (yes/no): ")
                            if refresh_choice.lower() in ['yes', 'y']:
                                refresh_cortex_search_service(session)
                        else:
                            print(f"\n❌ No records were removed for '{selected_file}'")
                    else:
                        print("❌ Operation cancelled")
                else:
                    print("❌ Invalid file number")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == "2":
            # Remove all orphaned files
            confirm = input(f"\n⚠️  Are you sure you want to remove ALL {len(orphaned_files)} orphaned files? (yes/no): ")
            if confirm.lower() in ['yes', 'y']:
                total_removed = 0
                
                for file in orphaned_files:
                    removed_counts = remove_file_from_tables(session, file)
                    total_removed += sum(removed_counts.values())
                
                if total_removed > 0:
                    print(f"\n✅ Successfully removed all orphaned files ({total_removed} total records)")
                    
                    refresh_choice = input("\n🔄 Refresh Cortex Search Service? (recommended) (yes/no): ")
                    if refresh_choice.lower() in ['yes', 'y']:
                        refresh_cortex_search_service(session)
                else:
                    print("\n❌ No records were removed")
            else:
                print("❌ Operation cancelled")
        
        elif choice == "3":
            print("❌ Operation cancelled")
        
        else:
            print("❌ Invalid choice")
        
        print("\n🎉 Cleanup process completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
