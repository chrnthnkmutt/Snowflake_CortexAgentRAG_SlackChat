# 🚀 Snowflake Cortex Agents Slack RAG Project

## 📋 Overview

This project implements a sophisticated **Retrieval-Augmented Generation (RAG)** system using Snowflake Cortex Agents integrated with Slack. It combines hybrid search and accurate SQL generation to provide AI-powered data interactions through a conversational interface.

**Recommend of reading the step of making project here: [Original QuickStart Guide](https://quickstarts.snowflake.com/guide/integrate_snowflake_cortex_agents_with_slack/index.html)**

**Key Features:**
- 🔍 **Document Search (RAG)**: Query PDF documents using vector similarity search
- 📊 **Data Analytics**: Generate SQL queries and visualizations from natural language
- 💬 **Slack Integration**: Conversational AI interface with rich message formatting
- 📈 **Chart Generation**: Automatic visualization of query results
- 🔐 **Secure Authentication**: JWT-based authentication with automatic token renewal

## 🏗️ Architecture

### RAG Pipeline
```
PDF Documents → Text Chunks → arctic-embed-m-v1.5 → 768D Vectors → Vector Search → Retrieved Context → LLM Generation
```

### Components
- **Embedding Model**: `arctic-embed-m-v1.5` (768 dimensions - Default)
- **LLM**: Claude-3.5-Sonnet
- **Vector Database**: Snowflake Cortex Search Service
- **Text Processing**: 1800-character chunks with 300-character overlap
- **Interface**: Slack Bot with Socket Mode

## 🧠 Embedding Model Details

### Default Model: arctic-embed-m-v1.5
- **Provider**: Snowflake's default embedding model for Cortex Search Service
- **Dimensions**: 768 (typical for arctic-embed-m models)
- **Type**: Multilingual embedding model
- **Architecture**: Transformer-based
- **Optimization**: Optimized for retrieval tasks
- **Performance**: Good balance between quality and computational efficiency
- **Usage**: Automatically applied when creating Cortex Search Service without explicit model specification

### Implementation in Project
The Cortex Search Service automatically uses this model for:
1. **Document Processing**: Converting PDF text chunks into vector embeddings
2. **Query Processing**: Converting user search queries into vectors
3. **Similarity Search**: Finding relevant document chunks based on vector similarity

### Key Benefits
1. **Managed Service**: No need to specify or configure embedding models
2. **Optimized Performance**: Pre-optimized for Snowflake's infrastructure
3. **Consistent Results**: Standardized embedding space across all searches
4. **Automatic Updates**: Model improvements handled by Snowflake

### Related Snowflake Functions
While the project doesn't explicitly use embedding functions, Snowflake provides:
- `SNOWFLAKE.CORTEX.EMBED_TEXT_768()` - for 768-dimension models like arctic-embed
- `SNOWFLAKE.CORTEX.EMBED_TEXT_1024()` - for 1024-dimension models
- `SNOWFLAKE.CORTEX.EMBED_TEXT_1536()` - for 1536-dimension models

### Verification Queries
To confirm the model and dimensions:
```sql
-- Check service details
DESCRIBE CORTEX SEARCH SERVICE DASH_DB.DASH_SCHEMA.VEHICLES_INFO;

-- Test embedding dimensions (if needed)
SELECT ARRAY_SIZE(SNOWFLAKE.CORTEX.EMBED_TEXT_768('arctic-embed-m-v1.5', 'test')) as dimensions;
```

## 🎯 Current Status & Next Steps

### ✅ **Completed**
- Core RAG architecture with Snowflake Cortex Search Service
- Slack bot integration with Socket Mode
- JWT authentication system
- PDF document processing and text chunking
- Dual-tool system: Document search + SQL generation
- Basic chart generation and file upload

### 🚀 **Priority Next Steps**

#### **🔧 1. Setup & Deployment (High Priority)**
- [ ] **Complete environment setup**
  - Upload PDF documents to `@DASH_DB.DASH_SCHEMA.DASH_PDFS` stage
  - Upload semantic model to `@DASH_DB.DASH_SCHEMA.DASH_SEMANTIC_MODELS` stage
  - Run `setup.sql` to create infrastructure
  - Run `cortex_search_service.sql` to build search service

- [ ] **Test basic functionality**
  - Run `test.py` to verify Cortex Agents API connection
  - Test Slack bot with simple queries
  - Verify both RAG and SQL generation work

#### **🐛 2. Fix Current Issues (High Priority)**
- [ ] **Complete missing implementations in `app.py`:**
  - Fix empty function implementations
  - Complete error handling logic
  - Improve chart generation robustness

- [ ] **Environment configuration:**
  - Verify all `.env` variables are correct
  - Test Snowflake connection and permissions
  - Validate Slack app tokens and permissions

#### **🔍 3. Testing & Validation (Medium Priority)**
- [ ] Create comprehensive test cases
- [ ] Performance optimization
- [ ] Response quality validation

#### **✨ 4. Feature Enhancements (Medium Priority)**
- [ ] Add conversation memory/context
- [ ] Implement better error messages
- [ ] Expand data sources and semantic model
- [ ] Improve visualization options

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

### Document Queries (RAG)
```
"What are the terms in the DataTires contract?"
"Summarize the ESG policy from Snowtires Automotive"
```

### Data Analytics
```
"Show me a breakdown of support tickets by service type"
"How many customers prefer email contact?"
```

### Hybrid Queries
```
"Compare our contract terms with customer complaints"
"Analyze support patterns mentioned in our agreements"
```

## 🔧 Development

### Key Components

#### **CortexChat Class** (`cortex_chat.py`)
- Handles Cortex Agents API communication
- Manages JWT authentication with automatic renewal
- Processes streaming responses (SSE)
- Parses tool results and citations

#### **Slack Bot** (`app.py`)
- Socket Mode integration for real-time messaging
- Rich message formatting with blocks
- Chart generation and file upload
- Error handling and user feedback

#### **Search Service** (`cortex_search_service.sql`)
- PDF document parsing and chunking
- Vector embedding with arctic-embed-m-v1.5
- Cortex Search Service configuration

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

### Embedding Model
- **Model**: arctic-embed-m-v1.5
- **Dimensions**: 768
- **Provider**: Snowflake (default for Cortex Search)
- **Optimization**: Retrieval tasks, multilingual support

### Semantic Model
- **6 Dimensions**: TICKET_ID, CUSTOMER_NAME, CUSTOMER_EMAIL, SERVICE_TYPE, REQUEST, CONTACT_PREFERENCE
- **Verified Queries**: Pre-tested SQL patterns for common analytics
- **Synonyms**: Multiple ways to reference each dimension

### Performance
- **Chunk Size**: 1800 characters with 300 overlap
- **Max Results**: Configurable (default: 1 for focused responses)
- **Target Lag**: 1 hour for search service updates

## 🎉 Success Metrics

**You'll know the system is working when:**
- ✅ Slack bot responds to messages without errors
- ✅ Document-based queries return relevant citations
- ✅ Data analysis queries generate accurate SQL and charts
- ✅ Users can interact naturally with the AI assistant
- ✅ System handles both RAG and analytics use cases seamlessly

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
