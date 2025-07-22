from typing import Any
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import snowflake.connector
import pandas as pd
from snowflake.core import Root
from dotenv import load_dotenv
import matplotlib
import matplotlib.pyplot as plt 
from snowflake.snowpark import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import *
import numpy as np
import cortex_chat
import time
import requests

matplotlib.use('Agg')
load_dotenv()

ACCOUNT = os.getenv("ACCOUNT")
HOST = os.getenv("HOST")
USER = os.getenv("DEMO_USER")
DATABASE = os.getenv("DEMO_DATABASE")
SCHEMA = os.getenv("DEMO_SCHEMA")
ROLE = os.getenv("DEMO_USER_ROLE")
WAREHOUSE = os.getenv("WAREHOUSE")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
AGENT_ENDPOINT = os.getenv("AGENT_ENDPOINT")
SEMANTIC_MODEL = os.getenv("SEMANTIC_MODEL")
SEARCH_SERVICE = os.getenv("SEARCH_SERVICE")
RSA_PRIVATE_KEY_PATH = os.getenv("RSA_PRIVATE_KEY_PATH")
MODEL = os.getenv("MODEL")

DEBUG = False

# Initializes app
app = App(token=SLACK_BOT_TOKEN)
messages = []

@app.message("hello")
def message_hello(message, say):
    build = """
Not a developer was stirring, all deep in the fight.
The code was deployed in the pipelines with care,
In hopes that the features would soon be there.

And execs, so eager to see the results,
Were prepping their speeches, avoiding the gulps.
When, what to my wondering eyes should appear,
But a slide-deck update, with a demo so clear!

And we shouted out to developers,
Let’s launch this build live and avoid any crash!
The demos they created, the videos they made,
Were polished and ready, the hype never delayed.
            """

    say(build)
    say(
        text = "Let's BUILD",
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f":snowflake: Let's BUILD!",
                }
            },
        ]                
    )

@app.event("message")
def handle_message_events(ack, body, say):
    try:
        ack()
        #channel_id = body['event']['channel']
        #get_chat_history = app.client.conversations_history(channel=channel_id, limit=20)
        prompt = body['event']['text']
        say(
            text = "Snowflake Cortex AI is generating a response",
            blocks=[
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": ":snowflake: Snowflake Cortex AI is generating a response. Please wait...",
                    }
                },
                {
                    "type": "divider"
                },
            ]
        )
        response = ask_agent(prompt)
        display_agent_response(response,say)
    except Exception as e:
        error_info = f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
        print(error_info)
        say(
            text = "Request failed...",
            blocks=[
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": f"{error_info}",
                    }
                },
                {
                    "type": "divider"
                },
            ]
        )        

def ask_agent(prompt):
    # Try to use the enhanced Cortex Chat first, fall back to vectorize_answer if needed
    try:
        # Use the cortex chat for better analytical responses
        resp = CORTEX_APP.chat(prompt)
        if resp and resp.get('text'):
            return resp
    except Exception as e:
        print(f"Cortex Chat failed, falling back to vectorize_answer: {e}")
    
    # Fallback to the vectorized search approach
    resp = vectorize_answer(prompt)
    return resp

def display_agent_response(content,say):
    if content['sql']:
        sql = content['sql']
        df = pd.read_sql(sql, CONN)
        say(
            text = "Answer:",
            blocks=[
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_quote",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Answer:",
                                    "style": {
                                        "bold": True
                                    }
                                }
                            ]
                        },
                        {
                            "type": "rich_text_preformatted",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": f"{df.to_string()}"
                                }
                            ]
                        }
                    ]
                }
            ]
        )
        
        # Enhanced chart generation logic
        chart_img_url = None
        should_create_chart = False
        
        # Check if chart is recommended by the AI response
        if content.get('chart_recommended', False):
            should_create_chart = True
        
        # Also check if data is suitable for charting (more than 1 column and appropriate data types)
        elif len(df.columns) >= 2:
            # Check if we have categorical and numerical data suitable for charting
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object', 'string']).columns
            
            if len(numerical_cols) >= 1 and len(categorical_cols) >= 1:
                should_create_chart = True
            elif len(df) <= 20 and len(numerical_cols) >= 1:  # Small dataset with numbers
                should_create_chart = True
        
        if should_create_chart:
            try:
                chart_img_url = plot_smart_chart(df)
            except Exception as e:
                error_info = f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
                print(f"Warning: Could not create chart. {error_info}")
                
        if chart_img_url is not None:
            say(
                text = "Chart",
                blocks=[
                    {
                        "type": "image",
                        "title": {
                            "type": "plain_text",
                            "text": "Data Visualization"
                        },
                        "block_id": "image",
                        "slack_file": {
                            "url": f"{chart_img_url}"
                        },
                        "alt_text": "Data Chart"
                    }
                ]
            )
    else:
        say(
            text = "Answer:",
            blocks = [
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_quote",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": f"Answer: {content['text']}",
                                    "style": {
                                        "bold": True
                                    }
                                }
                            ]
                        },
                        {
                            "type": "rich_text_quote",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": f"* Citation: {content['citations']}",
                                    "style": {
                                        "italic": True
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]                
        )

def plot_smart_chart(df):
    """Intelligently choose and create the best chart type based on the data."""
    plt.figure(figsize=(12, 8), facecolor='#333333')
    
    # Determine the best chart type based on data characteristics
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'string']).columns
    
    if len(df.columns) == 2 and len(categorical_cols) == 1 and len(numerical_cols) == 1:
        # Perfect for pie chart or bar chart
        cat_col = categorical_cols[0]
        num_col = numerical_cols[0]
        
        # If we have percentage-like data or parts of a whole, use pie chart
        if df[num_col].sum() <= 100 or len(df) <= 6:
            plt.pie(df[num_col], 
                    labels=df[cat_col], 
                    autopct='%1.1f%%', 
                    startangle=90, 
                    colors=plt.cm.Set3(np.linspace(0, 1, len(df))), 
                    textprops={'color':"white",'fontsize': 12})
            plt.title(f'{cat_col} Distribution', color='white', fontsize=16, pad=20)
        else:
            # Use bar chart for larger numbers
            bars = plt.bar(df[cat_col], df[num_col], 
                          color=plt.cm.Set3(np.linspace(0, 1, len(df))))
            plt.title(f'{cat_col} vs {num_col}', color='white', fontsize=16, pad=20)
            plt.xlabel(cat_col, color='white', fontsize=12)
            plt.ylabel(num_col, color='white', fontsize=12)
            plt.xticks(rotation=45, color='white')
            plt.yticks(color='white')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height}', ha='center', va='bottom', color='white')
                        
    elif len(numerical_cols) >= 2:
        # Multiple numerical columns - use grouped bar chart
        num_cols_to_plot = numerical_cols[:3]  # Limit to 3 columns for readability
        x = np.arange(len(df))
        width = 0.8 / len(num_cols_to_plot)
        
        for i, col in enumerate(num_cols_to_plot):
            offset = (i - len(num_cols_to_plot)/2) * width + width/2
            plt.bar(x + offset, df[col], width, label=col, alpha=0.8)
        
        plt.title('Multi-Variable Comparison', color='white', fontsize=16, pad=20)
        plt.xlabel('Records', color='white', fontsize=12)
        plt.ylabel('Values', color='white', fontsize=12)
        plt.xticks(x, [f'Record {i+1}' for i in range(len(df))], rotation=45, color='white')
        plt.yticks(color='white')
        plt.legend()
        
    else:
        # Default to the first two columns
        col1, col2 = df.columns[0], df.columns[1]
        plt.bar(df[col1], df[col2], 
                color=plt.cm.Set3(np.linspace(0, 1, len(df))))
        plt.title(f'{col1} vs {col2}', color='white', fontsize=16, pad=20)
        plt.xlabel(col1, color='white', fontsize=12)
        plt.ylabel(col2, color='white', fontsize=12)
        plt.xticks(rotation=45, color='white')
        plt.yticks(color='white')
    
    # Ensure equal aspect ratio for pie charts
    if 'pie' in str(plt.gca().get_children()):
        plt.axis('equal')
    
    # Set the background color for the plot area
    plt.gca().set_facecolor('#333333')   
    plt.tight_layout()

    # Save the chart
    file_path_jpg = 'smart_chart.jpg'
    plt.savefig(file_path_jpg, format='jpg', bbox_inches='tight', dpi=150)
    plt.close()  # Close the figure to free memory
    
    return upload_chart_to_slack(file_path_jpg)

def plot_chart(df):
    """Legacy pie chart function - kept for compatibility."""
    return plot_smart_chart(df)

def upload_chart_to_slack(file_path_jpg):
    """Upload chart image to Slack and return the URL."""
    file_size = os.path.getsize(file_path_jpg)

    # Upload image file to slack
    file_upload_url_response = app.client.files_getUploadURLExternal(filename=file_path_jpg, length=file_size)
    if DEBUG:
        print(file_upload_url_response)

    file_upload_url = file_upload_url_response['upload_url']
    file_id = file_upload_url_response['file_id']
    with open(file_path_jpg, 'rb') as f:
        response = requests.post(file_upload_url, files={'file': f})

    # Check the response
    img_url = None
    if response.status_code != 200:
        print("File upload failed", response.text)
    else:
        # Complete upload and get permalink to display
        response = app.client.files_completeUploadExternal(files=[{"id": file_id, "title": "chart"}])
        if DEBUG:
            print(response)
        img_url = response['files'][0]['permalink']
        time.sleep(2)
    
    return img_url

def init():
    conn,session,jwt,cortex_app = None,None,None,None

    conn = snowflake.connector.connect(
        user=USER,
        authenticator="SNOWFLAKE_JWT",
        private_key_file=RSA_PRIVATE_KEY_PATH,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        role=ROLE,
        host=HOST
    )

    connection_parameters = {
        "user":USER,
        "authenticator":"SNOWFLAKE_JWT",
        "private_key_file":RSA_PRIVATE_KEY_PATH,
        "account":ACCOUNT,
        "warehouse":WAREHOUSE,
        "database":DATABASE,
        "schema":SCHEMA,
        "role":ROLE,
        "host":HOST
    }

    session = Session.builder.configs(connection_parameters).create()
    if not conn.rest.token:
        print(">>>>>>>>>> Snowflake connection unsuccessful!")

    cortex_app = cortex_chat.CortexChat(
        AGENT_ENDPOINT, 
        SEARCH_SERVICE,
        SEMANTIC_MODEL,
        MODEL, 
        ACCOUNT,
        USER,
        RSA_PRIVATE_KEY_PATH)

    print(">>>>>>>>>> Init complete")
    return conn,session,jwt,cortex_app

def vectorize_answer(question):
    # Enhanced function to provide more analytical and calculated responses
    answer = 'There is no answer to this question'
    citations = ''
    SESSION.use_role("SYSADMIN")
    
    # First, check if this is a general knowledge question that doesn't need document context
    if is_general_question(question):
        # Answer general questions directly without document context
        general_answer = SESSION.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', '{question}') as ANSWER
        """).collect()[0]["ANSWER"]
        return {"sql": "", "text": str(general_answer), "citations": "General knowledge - no document citation needed"}
    
    # Enhanced prompt for analytical thinking
    analytical_prompt = f"""
    Question: {question}
    
    You are an analytical AI assistant. For this question:
    1. If it asks for breakdowns, comparisons, or calculations, provide specific numbers and percentages
    2. If it asks for visual representation (charts, graphs), recommend appropriate visualization
    3. Analyze patterns and provide insights, not just raw information
    4. Calculate derived metrics when possible (percentages, ratios, trends)
    5. Be analytical and computational in your response
    
    Based on the following document content, analyze and calculate the answer:
    """
    
    df = SESSION.table('DASH_DB.DASH_SCHEMA.VECTORIZED_PDFS')
    vector_search = df.with_column('QUESTION', F.lit(question))
    vector_search = vector_search.with_column('EMBEDQ', F.call_function('SNOWFLAKE.CORTEX.EMBED_TEXT_1024',
                                                    F.lit('voyage-multilingual-2'),
                                                    F.col('QUESTION'))).cache_result()
    vector_similar = vector_search.with_column('search', F.call_function('VECTOR_COSINE_SIMILARITY',
                                           F.col('EMBED'),
                                          F.col('EMBEDQ')))

    vector_similar = vector_similar.sort(F.col('SEARCH').desc()).limit(5).cache_result()  # Increased to 5 for better context

    # Check if the similarity score is too low (meaning the question is not related to documents)
    top_similarity = vector_similar.select(F.col('SEARCH')).limit(1).collect()[0]["SEARCH"]
    
    if top_similarity < 0.25:  # Slightly lowered threshold for better coverage
        # Question doesn't match document content well, answer as general knowledge
        enhanced_general_prompt = f"""
        {question}
        
        Please provide a calculated, analytical answer. If this involves numbers, calculations, or comparisons, 
        provide specific figures and analysis rather than general statements.
        """
        general_answer = SESSION.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', '{enhanced_general_prompt}') as ANSWER
        """).collect()[0]["ANSWER"]
        return {"sql": "", "text": str(general_answer), "citations": "General knowledge - no document citation needed"}

    citations = vector_similar.select_expr("LISTAGG(TITLE, ';') AS ALL_TITLES").collect()[0]["ALL_TITLES"]

    # Limit the context size to avoid token limits - take first 6000 characters from each relevant document
    vector_relevent = vector_similar.select(F.array_agg(F.substr(F.col('OBJECT'), 1, 6000)).alias('OBJECT'))

    # Enhanced analytical prompt
    enhanced_prompt = analytical_prompt + """
    
    Document Content:
    """ + """
    
    Please analyze this information and provide:
    - Specific calculations and numbers where applicable
    - Percentages and ratios when relevant
    - Clear analytical insights
    - If the question asks for comparisons or breakdowns, calculate and present them clearly
    - If visualization would be helpful, mention what type of chart would be appropriate
    
    Answer:"""

    answer = vector_relevent.with_column('ANSWER',
                                    F.call_function('SNOWFLAKE.CORTEX.COMPLETE', F.lit('claude-3-5-sonnet'),
                                                   F.concat(F.lit(enhanced_prompt),
                                                           F.col('OBJECT').astype(StringType()))))

    answer_text = str(answer.select('ANSWER').limit(1).collect()[0]["ANSWER"])
    
    # Check if the response recommends creating a chart
    chart_recommended = any(keyword in answer_text.lower() for keyword in 
                          ['chart', 'graph', 'visualization', 'plot', 'pie chart', 'bar chart', 'line chart'])

    return {
        "sql": "", 
        "text": answer_text, 
        "citations": citations,
        "chart_recommended": chart_recommended
    }

def is_general_question(question):
    """Check if the question is a general knowledge question that doesn't require document context"""
    question_lower = question.lower().strip()
    
    # Math patterns
    math_patterns = [
        r'\d+\s*[\+\-\*\/]\s*\d+',  # Simple math like "2+2", "10-5"
        r'what\s+is\s+\d+',          # "what is 5+5"
        r'calculate.*\d+\s*[\+\-\*\/]\s*\d+',  # "calculate 10*3"
        r'solve.*\d+\s*[\+\-\*\/]',   # "solve 15/3"
    ]
    
    # General knowledge patterns that don't relate to business documents
    general_patterns = [
        r'what\s+is\s+the\s+capital',    # "what is the capital of..."
        r'who\s+is\s+the\s+president',   # "who is the president of..."
        r'when\s+was.*founded',          # "when was... founded"
        r'how\s+many\s+days\s+in\s+a\s+year',  # "how many days in a year"
        r'what\s+year\s+did.*happen',    # "what year did... happen"
        r'define\s+\w+$',                # "define something" (single word)
        r'meaning\s+of\s+\w+$',          # "meaning of something" (single word)
        r'how\s+do\s+you\s+cook',        # "how do you cook..."
        r'what\s+is\s+the\s+weather',    # "what is the weather..."
    ]
    
    # Business/analytical patterns that SHOULD use documents
    business_patterns = [
        r'support\s+ticket',             # "support ticket breakdown"
        r'customer.*service',            # "customer service breakdown"
        r'breakdown.*by',                # "breakdown by service type"
        r'compare.*service',             # "compare services"
        r'cellular.*business',           # "cellular vs business"
        r'contract.*tire',               # Contract/tire related questions
        r'recycling.*rubber',            # Recycling related questions
        r'percentage.*customers',        # Customer percentage questions
        r'how\s+many.*customers',        # Customer count questions
        r'total.*tickets',               # Ticket count questions
    ]
    
    import re
    
    # Check if it's a business question first (should NOT be treated as general)
    for pattern in business_patterns:
        if re.search(pattern, question_lower):
            return False
    
    # Then check for general knowledge patterns
    all_general_patterns = math_patterns + general_patterns
    for pattern in all_general_patterns:
        if re.search(pattern, question_lower):
            return True
    
    return False

# Start app
if __name__ == "__main__":
    CONN,SESSION, JWT,CORTEX_APP = init()
    Root = Root(CONN)
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
