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
    resp = vectorize_answer(prompt)
    #resp = CORTEX_APP.chat(prompt)
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
        if len(df.columns) > 1:
            chart_img_url = None
            try:
                chart_img_url = plot_chart(df)
            except Exception as e:
                error_info = f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
                print(f"Warning: Data likely not suitable for displaying as a chart. {error_info}")
            if chart_img_url is not None:
                say(
                    text = "Chart",
                    blocks=[
                        {
                            "type": "image",
                            "title": {
                                "type": "plain_text",
                                "text": "Chart"
                            },
                            "block_id": "image",
                            "slack_file": {
                                "url": f"{chart_img_url}"
                            },
                            "alt_text": "Chart"
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

def plot_chart(df):
    plt.figure(figsize=(10, 6), facecolor='#333333')

    # plot pie chart with percentages, using dynamic column names
    plt.pie(df[df.columns[1]], 
            labels=df[df.columns[0]], 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=['#1f77b4', '#ff7f0e'], 
            textprops={'color':"white",'fontsize': 16})

    # ensure equal aspect ratio
    plt.axis('equal')
    # set the background color for the plot area to dark as well
    plt.gca().set_facecolor('#333333')   
    plt.tight_layout()

    # save the chart as a .jpg file
    file_path_jpg = 'pie_chart.jpg'
    plt.savefig(file_path_jpg, format='jpg')
    file_size = os.path.getsize(file_path_jpg)

    # upload image file to slack
    file_upload_url_response = app.client.files_getUploadURLExternal(filename=file_path_jpg,length=file_size)
    if DEBUG:
        print(file_upload_url_response)
    file_upload_url = file_upload_url_response['upload_url']
    file_id = file_upload_url_response['file_id']
    with open(file_path_jpg, 'rb') as f:
        response = requests.post(file_upload_url, files={'file': f})

    # check the response
    img_url = None
    if response.status_code != 200:
        print("File upload failed", response.text)
    else:
        # complete upload and get permalink to display
        response = app.client.files_completeUploadExternal(files=[{"id":file_id, "title":"chart"}])
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
    # Vectorize the answer using the Snowflake function
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
    
    df = SESSION.table('DASH_DB.DASH_SCHEMA.VECTORIZED_PDFS')
    vector_search = df.with_column('QUESTION',F.lit(question))
    vector_search = vector_search.with_column('EMBEDQ',F.call_function('SNOWFLAKE.CORTEX.EMBED_TEXT_1024',
                                                    F.lit('voyage-multilingual-2'),
                                                    F.col('QUESTION'))).cache_result()
    vector_similar = vector_search.with_column('search',F.call_function('VECTOR_COSINE_SIMILARITY'
                                           ,F.col('EMBED'),
                                          F.col('EMBEDQ')))

    vector_similar = vector_similar.sort(F.col('SEARCH').desc()).limit(3).cache_result()

    # Check if the similarity score is too low (meaning the question is not related to documents)
    top_similarity = vector_similar.select(F.col('SEARCH')).limit(1).collect()[0]["SEARCH"]
    
    if top_similarity < 0.3:  # Low similarity threshold
        # Question doesn't match document content well, answer as general knowledge
        general_answer = SESSION.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', '{question}') as ANSWER
        """).collect()[0]["ANSWER"]
        return {"sql": "", "text": str(general_answer), "citations": "General knowledge - no document citation needed"}

    citations = vector_similar.select_expr("LISTAGG(TITLE, ';') AS ALL_TITLES").collect()[0]["ALL_TITLES"]

    vector_similar.select('OBJECT','QUESTION')
    ### link to the different llm functions and what region supports them - https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions

    # Limit the context size to avoid token limits - take first 5000 characters from each relevant document
    vector_relevent = vector_similar.select(F.array_agg(F.substr(F.col('OBJECT'), 1, 5000)).alias('OBJECT'))

    answer = vector_relevent.with_column('ANSWER',
                                    F.call_function('SNOWFLAKE.CORTEX.COMPLETE',F.lit('claude-3-5-sonnet'),
                                                   F.concat(F.lit('Question: '), F.lit(question),
                                                           F.lit('\n\nBased on the following document content, please answer the question. If the question cannot be answered from the provided documents, say so clearly:\n\n'),
                                                           F.col('OBJECT').astype(StringType()),
                                                           F.lit('\n\nAnswer:'))))

    return {"sql": "", "text": str(answer.select('ANSWER').limit(1).collect()[0]["ANSWER"]), "citations": citations}

def is_general_question(question):
    """Check if the question is a general knowledge question that doesn't require document context"""
    question_lower = question.lower().strip()
    
    # Math patterns
    math_patterns = [
        r'\d+\s*[\+\-\*\/]\s*\d+',  # Simple math like "2+2", "10-5"
        r'what\s+is\s+\d+',          # "what is 5+5"
        r'calculate',                 # "calculate 10*3"
        r'solve.*\d',                # "solve 15/3"
    ]
    
    # General knowledge patterns
    general_patterns = [
        r'what\s+is\s+the\s+capital',    # "what is the capital of..."
        r'who\s+is',                      # "who is..."
        r'when\s+was',                    # "when was..."
        r'how\s+many\s+days',             # "how many days in a year"
        r'what\s+year',                   # "what year..."
        r'define\s+',                     # "define..."
        r'meaning\s+of',                  # "meaning of..."
    ]
    
    import re
    all_patterns = math_patterns + general_patterns
    
    for pattern in all_patterns:
        if re.search(pattern, question_lower):
            return True
    
    return False

# Start app
if __name__ == "__main__":
    CONN,SESSION, JWT,CORTEX_APP = init()
    Root = Root(CONN)
    SocketModeHandler(app, SLACK_APP_TOKEN).start()