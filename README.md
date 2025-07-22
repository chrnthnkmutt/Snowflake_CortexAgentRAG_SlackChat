# 🚀 Snowflake Cortex Agents Slack RAG Project

## 📋 Overview

This project implements a sophisticated **Retrieval-Augmented Generation (RAG)** system using Snowflake Cortex Agents integrated with Slack. It combines intelligent question routing, vector similarity search, and accurate data analytics to provide AI-powered interactions through a conversational interface.

**Recommend reading the step-by-step project guide here: [Original QuickStart Guide](https://quickstarts.snowflake.com/guide/integrate_snowflake_cortex_agents_with_slack/index.html)**

**Key Features:**
- 🧠 **Intelligent Question Routing**: Automatically detects general knowledge vs document-specific questions
- 🔍 **Document Search (RAG)**: Query PDF documents using vector similarity search with 1024-dimensional embeddings
- 📊 **Data Analytics**: Generate SQL queries and visualizations from natural language
- 💬 **Slack Integration**: Conversational AI interface with rich message formatting
- 📈 **Chart Generation**: Automatic visualization of query results
- 🔐 **Secure Authentication**: JWT-based authentication with automatic token renewal
- ⚡ **Hybrid Intelligence**: Seamlessly switches between document-based and general knowledge responses

## 🏗️ Architecture

### Enhanced RAG Pipeline
```
Question → Intelligent Router → [General Knowledge: Direct LLM] OR [Document-Specific: PDF Documents → voyage-multilingual-2 → 1024D Vectors → Similarity Search (>0.3) → Retrieved Context → LLM Generation]
```

### Components
- **Embedding Model**: `voyage-multilingual-2` (1024 dimensions)
- **LLM**: Claude-3.5-Sonnet (consistent across all responses)
- **Vector Database**: Snowflake Cortex Search Service with custom vectorization
- **Text Processing**: 1800-character chunks with 300-character overlap  
- **Intelligent Routing**: Pattern-based detection for math, general knowledge, and document queries
- **Similarity Threshold**: 0.3 minimum for document relevance
- **Interface**: Slack Bot with Socket Mode

## 🧠 Embedding Model Details

### Current Model: voyage-multilingual-2
- **Provider**: Snowflake Cortex (`SNOWFLAKE.CORTEX.EMBED_TEXT_1024`)
- **Dimensions**: 1024 (high-quality embedding space)
- **Type**: Multilingual embedding model optimized for retrieval
- **Usage**: Custom implementation in `vectorize_answer()` function
- **Performance**: Superior semantic understanding with larger vector space

### Key Implementation Features

#### **Intelligent Question Routing**
The system automatically categorizes questions and routes them appropriately:

1. **Mathematical Queries**: `"2+2"`, `"calculate 10*5"` → Direct LLM response
2. **General Knowledge**: `"What is the capital of France?"` → Direct LLM response  
3. **Document-Specific**: `"What are the contract terms?"` → RAG pipeline with PDF search
4. **Low Similarity**: Questions with <0.3 similarity to documents → Fallback to general knowledge

#### **Vector Similarity Processing**
```python
# Custom vectorization with voyage-multilingual-2 (1024D)
vector_search.with_column('EMBEDQ', F.call_function('SNOWFLAKE.CORTEX.EMBED_TEXT_1024', 
                                                   F.lit('voyage-multilingual-2'), 
                                                   F.col('QUESTION')))

# Similarity threshold filtering
if top_similarity < 0.3:  # Smart fallback to general knowledge
    return direct_llm_response(question)
```

#### **Token Optimization**
- **Document Chunks**: Limited to 5,000 characters per document to prevent token overflow
- **Context Window**: Optimized prompting to stay within Claude-3.5-Sonnet's limits
- **Efficient Aggregation**: Smart text concatenation with proper formatting

## 🎯 Current Status & Next Steps

### ✅ **Completed**
- ✅ **Enhanced RAG Architecture**: Custom vectorization with voyage-multilingual-2 (1024D)
- ✅ **Intelligent Question Routing**: Automatic detection of general vs document-specific queries
- ✅ **Slack Bot Integration**: Socket Mode with rich message formatting
- ✅ **JWT Authentication**: Secure authentication system
- ✅ **PDF Document Processing**: Text chunking and vectorization
- ✅ **Smart Similarity Filtering**: 0.3 threshold for document relevance
- ✅ **Consistent Model Usage**: Claude-3.5-Sonnet across all LLM calls
- ✅ **Token Optimization**: 5K character limits to prevent overflow
- ✅ **Chart Generation**: Automatic visualization of query results

### 🚀 **Priority Next Steps**

#### **🔧 1. Setup & Deployment (High Priority)**
- [ ] **Complete environment setup**
  - Upload PDF documents to `@DASH_DB.DASH_SCHEMA.DASH_PDFS` stage
  - Upload semantic model to `@DASH_DB.DASH_SCHEMA.DASH_SEMANTIC_MODELS` stage
  - Run `setup.sql` to create infrastructure
  - Run `cortex_search_service.sql` to build search service with voyage-multilingual-2

- [ ] **Test enhanced functionality**
  - Test mathematical queries: `"What is 2+2?"` (should return 4 directly)
  - Test general knowledge: `"What is the capital of France?"` (should return Paris)
  - Test document queries: `"What are the contract terms?"` (should search PDFs)
  - Verify similarity threshold works for unrelated queries

#### **🐛 2. Optimize Current Implementation (Medium Priority)**
- [ ] **Fine-tune similarity threshold**: Test 0.2, 0.3, 0.4 thresholds for optimal routing
- [ ] **Expand general knowledge patterns**: Add more regex patterns for better detection
- [ ] **Performance optimization**: Cache embeddings for common queries
- [ ] **Error handling**: Improve robustness for edge cases

#### **✨ 3. Feature Enhancements (Medium Priority)**
- [ ] **Conversation Memory**: Add context awareness across messages
- [ ] **Advanced Analytics**: Support complex multi-step queries
- [ ] **Custom Visualizations**: Expand beyond pie charts
- [ ] **Real-time Learning**: Adapt similarity thresholds based on user feedback

## 🛠️ Quick Start

### Prerequisites
- Snowflake account with Cortex features enabled
- Slack workspace and app tokens
- Python 3.8+

### Installation
```bash
# 1. Clone the repository
git clone <repository-url>
cd cortext-agent-slack-chat-RAG

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# 4. Set up Snowflake infrastructure
snowsql -f setup.sql
snowsql -f cortex_search_service.sql

# 5. Test the connection
python test.py

# 6. Run the Slack bot
python app.py
```

### Environment Variables
```bash
DEMO_DATABASE='DASH_DB'
DEMO_SCHEMA='DASH_SCHEMA'
WAREHOUSE='DASH_S'
DEMO_USER='your_username'
DEMO_USER_ROLE='ACCOUNTADMIN'
SEMANTIC_MODEL='@DASH_DB.DASH_SCHEMA.DASH_SEMANTIC_MODELS/support_tickets_semantic_model.yaml'
SEARCH_SERVICE='DASH_DB.DASH_SCHEMA.vehicles_info'
ACCOUNT='your_account_identifier'
HOST='your_account.snowflakecomputing.com'
AGENT_ENDPOINT='https://your_account.snowflakecomputing.com/api/v2/cortex/agent:run'
SLACK_APP_TOKEN="xapp-your-app-token"
SLACK_BOT_TOKEN="xoxb-your-bot-token"
RSA_PRIVATE_KEY_PATH='rsa_key.p8'
MODEL='claude-3-5-sonnet'
```

## 📁 Project Structure

```
├── app.py                          # Main Slack bot application
├── cortex_chat.py                  # Cortex Agents API client
├── generate_jwt.py                 # JWT token generation
├── setup.sql                       # Snowflake infrastructure setup
├── cortex_search_service.sql       # Search service creation
├── support_tickets_semantic_model.yaml  # Semantic model definition
├── test.py                         # API connection testing
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── data/                          # PDF documents for RAG
└── README.md                      # This file
```

## 🎮 Usage Examples

### Mathematical & General Knowledge Queries
```
"What is 2+2?"                          → Direct response: "4"
"Calculate 15 * 8"                      → Direct response: "120"
"What is the capital of France?"        → Direct response: "Paris"
"Who invented the telephone?"           → Direct response: Historical information
```

### Document-Specific Queries (RAG)
```
"What are the terms in the DataTires contract?"          → Searches PDFs, returns relevant sections
"Summarize the ESG policy from Snowtires Automotive"    → Vector search + document analysis
"What recycling procedures are mentioned?"              → PDF content with citations
```

### Smart Routing Examples
```
"Tell me about Python programming"       → General knowledge (low similarity to business docs)
"What are our payment terms?"           → Document search (high similarity to contracts)
"Compare machine learning models"       → General knowledge (no relevant business docs)
```

### Data Analytics (SQL Generation)
```
"Show me a breakdown of support tickets by service type"
"How many customers prefer email contact?"
"Create a chart of customer distribution"
```

## 🔧 Development

### Key Components

#### **Enhanced Vectorize Answer Function** (`app.py`)
- **Intelligent Question Routing**: Automatically detects math, general knowledge, and document queries
- **Custom Vector Search**: Uses voyage-multilingual-2 with 1024-dimensional embeddings
- **Similarity Threshold**: 0.3 minimum for document relevance detection
- **Token Management**: 5,000 character limit per document to prevent overflow
- **Consistent LLM**: Claude-3.5-Sonnet for all text generation

#### **CortexChat Class** (`cortex_chat.py`)
- Handles Cortex Agents API communication (alternative approach)
- Manages JWT authentication with automatic renewal
- Processes streaming responses (SSE)
- Parses tool results and citations

#### **Slack Bot** (`app.py`)
- Socket Mode integration for real-time messaging
- Rich message formatting with blocks
- Chart generation and file upload
- Comprehensive error handling and user feedback

#### **Custom Vector Search** (`cortex_search_service.sql`)
- PDF document parsing and chunking
- **Updated**: Vector embedding with voyage-multilingual-2 (1024D)
- Enhanced similarity search with threshold filtering

### Testing
```bash
# Test Cortex Agents API
python test.py

# Test individual components
python -c "from cortex_chat import CortexChat; print('Import successful')"

# Debug mode
# Set DEBUG = True in cortex_chat.py for detailed logging
```

## 📊 Technical Details

### Enhanced Embedding Implementation
- **Model**: voyage-multilingual-2 (via `SNOWFLAKE.CORTEX.EMBED_TEXT_1024`)
- **Dimensions**: 1024 (upgraded from 768 for better semantic understanding)
- **Implementation**: Custom vectorization in `vectorize_answer()` function
- **Optimization**: High-quality retrieval with multilingual support

### Intelligent Question Classification
```python
# Mathematical patterns: "2+2", "calculate 10*5"
# General knowledge: "capital of France", "who invented..."
# Document-specific: High similarity (>0.3) to PDF content
# Fallback: Low similarity (<0.3) → General knowledge mode
```

### Smart Similarity Threshold
- **Threshold**: 0.3 cosine similarity minimum for document relevance
- **Above 0.3**: Uses RAG pipeline with PDF content and citations
- **Below 0.3**: Falls back to general knowledge mode
- **Benefits**: Prevents irrelevant document content from polluting responses

### Token Optimization Strategy
- **Document Chunks**: 5,000 characters per document (reduced from 10,000)
- **Context Window**: Optimized prompting for Claude-3.5-Sonnet
- **Aggregation**: Smart text concatenation with proper formatting
- **Fallback**: Automatic token limit handling with graceful degradation

### Semantic Model
- **6 Dimensions**: TICKET_ID, CUSTOMER_NAME, CUSTOMER_EMAIL, SERVICE_TYPE, REQUEST, CONTACT_PREFERENCE
- **Verified Queries**: Pre-tested SQL patterns for common analytics
- **Synonyms**: Multiple ways to reference each dimension

### Performance Characteristics
- **Chunk Size**: 1800 characters with 300 overlap
- **Vector Comparison**: VECTOR_COSINE_SIMILARITY with 1024D vectors
- **Response Types**: Direct LLM, RAG with citations, or SQL generation
- **Target Lag**: 1 hour for search service updates

## 🎉 Success Metrics

**You'll know the enhanced system is working when:**
- ✅ **Smart Routing**: Math questions like "2+2" return "4" instantly without searching documents
- ✅ **General Knowledge**: Questions like "What is the capital of France?" return "Paris" directly
- ✅ **Document Search**: Business queries return relevant PDF content with proper citations
- ✅ **Similarity Filtering**: Unrelated questions gracefully fall back to general knowledge mode
- ✅ **No Token Errors**: System handles large documents without "max tokens exceeded" errors
- ✅ **Consistent Quality**: All responses use Claude-3.5-Sonnet for consistent, high-quality output
- ✅ **Slack Integration**: Rich message formatting with charts and error handling
- ✅ **Performance**: Fast responses due to intelligent routing and optimized token usage

### Testing Checklist
```bash
# Test mathematical queries
"What is 5 + 3?"                    # Should return: 8

# Test general knowledge  
"What is the capital of Japan?"     # Should return: Tokyo

# Test document-specific queries
"What are our contract terms?"      # Should search PDFs and return relevant content

# Test similarity threshold
"Explain quantum physics"           # Should fall back to general knowledge (low similarity)

# Test data analytics
"Show support ticket breakdown"     # Should generate SQL and charts
```

## 📚 Resources

- [Snowflake Cortex Agents Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- [Slack Bolt Python Framework](https://slack.dev/bolt-python/tutorial/getting-started)
- [Original QuickStart Guide](https://quickstarts.snowflake.com/guide/integrate_snowflake_cortex_agents_with_slack/index.html)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of Snowflake Labs and follows the associated licensing terms.
