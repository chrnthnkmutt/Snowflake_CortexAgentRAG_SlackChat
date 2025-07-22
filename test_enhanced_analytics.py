#!/usr/bin/env python3
"""
Test script for enhanced analytical capabilities of the Cortex Chat system.
This script tests various types of analytical questions to ensure the system
provides calculated responses rather than just document citations.
"""

import os
from dotenv import load_dotenv
import cortex_chat
import app
from snowflake.snowpark import Session

load_dotenv()

# Configuration
ACCOUNT = os.getenv("ACCOUNT")
HOST = os.getenv("HOST")
USER = os.getenv("DEMO_USER")
DATABASE = os.getenv("DEMO_DATABASE")
SCHEMA = os.getenv("DEMO_SCHEMA")
ROLE = os.getenv("DEMO_USER_ROLE")
WAREHOUSE = os.getenv("WAREHOUSE")
AGENT_ENDPOINT = os.getenv("AGENT_ENDPOINT")
SEMANTIC_MODEL = os.getenv("SEMANTIC_MODEL")
SEARCH_SERVICE = os.getenv("SEARCH_SERVICE")
RSA_PRIVATE_KEY_PATH = os.getenv("RSA_PRIVATE_KEY_PATH")
MODEL = os.getenv("MODEL")

def test_analytical_questions():
    """Test various analytical questions to verify enhanced capabilities."""
    
    print("🧪 Testing Enhanced Analytical Capabilities")
    print("=" * 60)
    
    # Initialize the enhanced cortex chat
    cortex_app = cortex_chat.CortexChat(
        AGENT_ENDPOINT, 
        SEARCH_SERVICE,
        SEMANTIC_MODEL,
        MODEL, 
        ACCOUNT,
        USER,
        RSA_PRIVATE_KEY_PATH
    )
    
    # Test questions that should generate analytical responses
    test_questions = [
        {
            "question": "Can you show me a breakdown of customer support tickets by service type cellular vs business internet?",
            "expected_behavior": "Should calculate specific numbers and percentages, recommend chart"
        },
        {
            "question": "What percentage of tickets are for cellular service vs business internet?",
            "expected_behavior": "Should provide calculated percentages"
        },
        {
            "question": "Create a chart showing the distribution of support tickets by service type",
            "expected_behavior": "Should recommend visualization and provide data for charting"
        },
        {
            "question": "Compare the recycling efficiency between rubber tires and carbon black",
            "expected_behavior": "Should calculate and compare percentages from documents"
        },
        {
            "question": "What is the most effective tire recycling method based on recovery rates?",
            "expected_behavior": "Should analyze and calculate which method is most effective"
        }
    ]
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}: {test_case['question']}")
        print(f"Expected: {test_case['expected_behavior']}")
        print("-" * 50)
        
        try:
            response = cortex_app.chat(test_case['question'])
            
            if response:
                print(f"✅ Response received:")
                print(f"📝 Text: {response.get('text', 'N/A')[:200]}...")
                print(f"📊 SQL Generated: {'Yes' if response.get('sql') else 'No'}")
                print(f"📈 Chart Recommended: {'Yes' if response.get('chart_recommended') else 'No'}")
                print(f"📚 Citations: {response.get('citations', 'N/A')[:100]}...")
                
                # Analyze response quality
                text = response.get('text', '').lower()
                has_calculations = any(keyword in text for keyword in ['%', 'percent', 'calculate', 'total', 'ratio'])
                has_analysis = any(keyword in text for keyword in ['analysis', 'compare', 'most', 'effective', 'better'])
                
                print(f"🧮 Contains Calculations: {'Yes' if has_calculations else 'No'}")
                print(f"🔍 Contains Analysis: {'Yes' if has_analysis else 'No'}")
                
            else:
                print("❌ No response received")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Testing Complete!")

def test_chart_generation_logic():
    """Test the smart chart generation logic."""
    
    print("\n📊 Testing Chart Generation Logic")
    print("=" * 40)
    
    import pandas as pd
    import numpy as np
    
    # Test data scenarios
    test_datasets = [
        {
            "name": "Service Type Breakdown",
            "data": pd.DataFrame({
                'Service_Type': ['Cellular', 'Business Internet', 'Home Internet'],
                'Ticket_Count': [45, 30, 25]
            }),
            "expected_chart": "Pie Chart (good for percentages)"
        },
        {
            "name": "Monthly Trends",
            "data": pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
                'Tickets': [120, 145, 132, 167],
                'Resolved': [115, 140, 128, 160]
            }),
            "expected_chart": "Bar Chart (multiple metrics)"
        },
        {
            "name": "Simple Comparison", 
            "data": pd.DataFrame({
                'Category': ['Type A', 'Type B'],
                'Value': [75, 125]
            }),
            "expected_chart": "Bar Chart or Pie Chart"
        }
    ]
    
    for test_data in test_datasets:
        print(f"\n📈 Testing: {test_data['name']}")
        print(f"Expected: {test_data['expected_chart']}")
        print(f"Data shape: {test_data['data'].shape}")
        print(f"Columns: {list(test_data['data'].columns)}")
        
        # Test the smart chart logic (without actually creating charts)
        df = test_data['data']
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'string']).columns
        
        print(f"Numerical columns: {list(numerical_cols)}")
        print(f"Categorical columns: {list(categorical_cols)}")
        
        # Determine chart type logic
        if len(df.columns) == 2 and len(categorical_cols) == 1 and len(numerical_cols) == 1:
            if df[numerical_cols[0]].sum() <= 100 or len(df) <= 6:
                chart_type = "Pie Chart"
            else:
                chart_type = "Bar Chart"
        elif len(numerical_cols) >= 2:
            chart_type = "Grouped Bar Chart"
        else:
            chart_type = "Default Bar Chart"
            
        print(f"✅ Recommended chart type: {chart_type}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Analytics Test Suite")
    
    try:
        test_analytical_questions()
        test_chart_generation_logic()
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Test suite completed!")
