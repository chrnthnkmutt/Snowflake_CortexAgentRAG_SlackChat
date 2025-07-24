# 🚀 Snowflake Cortex Agent RAG Slack Chat (Public Released Version)

## 📋 Overview

This project implements an intelligent **Retrieval-Augmented Generation (RAG)** system powered by Snowflake Cortex AI and integrated with Slack for conversational interactions. The system combines advanced vector search, intelligent question routing, data analytics, and visualization capabilities to deliver AI-powered assistance through a seamless chat interface.

**📚 Based on Snowflake QuickStart: [Integrate Snowflake Cortex Agents with Slack](https://quickstarts.snowflake.com/guide/integrate_snowflake_cortex_agents_with_slack/index.html)**

## ✨ Key Features

- 🧠 **Intelligent Question Routing**: Automatically classifies and routes questions between general knowledge, math calculations, and document-specific queries
- 🔍 **Advanced Document RAG**: Vector similarity search across PDF documents using `voyage-multilingual-2` embeddings (1024 dimensions)
- 📊 **Data Analytics & Visualization**: Natural language to SQL generation with automatic chart creation and Slack file uploads
- 🧮 **Multi-Modal Intelligence**: Handles mathematical calculations, general knowledge, and business document queries seamlessly  
- 💬 **Rich Slack Integration**: Interactive chat with formatted responses, file uploads, and error handling
- 🎯 **Smart Visualization**: Auto-generates pie charts for analytical results with dynamic data visualization
- 🔐 **Enterprise Security**: JWT-based authentication with RSA key pairs and automatic token management
- ⚡ **Performance Optimized**: Similarity thresholds, token management, and efficient vector operations
- 🌐 **Advanced Multilingual Support**: Intelligent language detection with automatic response matching across all query types
- 📝 **Enhanced Prompting System**: Sophisticated prompt engineering for consistent, high-quality responses in multiple languages

## 🏗️ Architecture Overview

### System Architecture
```
Slack User Input
       ↓
Question Classification Engine
       ↓
┌─────────────────┬─────────────────┬─────────────────┐
│  General/Math   │  Document RAG   │  Data Analytics │
│     Queries     │    Queries      │    Queries      │
└─────────────────┴─────────────────┴─────────────────┘
       ↓                   ↓                   ↓
Direct LLM Response    Vector Search      SQL Generation
       ↓                   ↓                   ↓
   Text Answer        PDF Context +       Tabular Data +
                      Citations           Auto Charts
       ↓                   ↓                   ↓
           Formatted Slack Response
```

### Core Components

- **Embedding Model**: `voyage-multilingual-2` (1024-dimensional vectors)
- **LLM Engine**: Claude-3.5-Sonnet (consistent across all response types)
- **Vector Database**: Snowflake with VECTOR_COSINE_SIMILARITY search
- **Text Processing**: 1800-character chunks with 300-character overlap
- **Similarity Threshold**: 0.3 minimum for document relevance detection
- **Interface**: Slack Bot with Socket Mode for real-time messaging
- **Authentication**: JWT with RSA key pairs for enterprise security
- **Language Intelligence**: Advanced multilingual prompting with automatic language detection and response matching

### Intelligent Routing Logic

1. **Mathematical Queries**: Pattern detection for calculations → Direct computation
2. **General Knowledge**: Low document similarity (<0.3) → Direct LLM response
3. **Document-Specific**: High similarity (≥0.3) → RAG pipeline with citations
4. **Analytics Queries**: Semantic model matching → SQL generation + visualization

## 🌐 Advanced Multilingual Intelligence

### Intelligent Language Detection & Response Matching

The system now features **sophisticated multilingual capabilities** that automatically detect the user's language and respond in the same language across all query types:

#### **Key Multilingual Features:**
- 🔤 **Automatic Language Detection**: Recognizes user's input language without explicit specification
- 🗣️ **Response Language Matching**: AI responds in the exact same language as the user's question
- 🌍 **Universal Language Support**: Works with Thai, English, Spanish, French, German, Chinese, Japanese, and many other languages
- 📚 **Consistent Across Query Types**: Language matching works for document RAG, general knowledge, and data analytics
- 🎯 **Professional Tone Preservation**: Maintains business-appropriate tone while matching user's language

#### **Multilingual Query Examples:**

**Thai Language Support:**
```
User: "บริษัทเรามีสัญญากับ DataTires ไหม?"
Bot: [Responds in Thai with document search results]

User: "แสดงตั๋วการสนับสนุนตามประเภทบริการ"
Bot: [Thai response with data analytics and charts]

User: "5+3 เท่ากับเท่าไร?"
Bot: "5+3 เท่ากับ 8"
```

**English Language Support:**
```
User: "What contracts do we have with suppliers?"
Bot: [English response with PDF search and citations]

User: "Show me support tickets by service type"
Bot: [English response with SQL data and visualization]

User: "What is 2+2?"
Bot: "2+2 equals 4"
```

**Spanish Language Support:**
```
User: "¿Cuáles son nuestros términos contractuales con proveedores?"
Bot: [Spanish response with document analysis]

User: "¿Cuánto es 10 × 7?"
Bot: "10 × 7 es igual a 70"
```

#### **Enhanced Prompting Architecture:**

The system uses **advanced prompt engineering** to ensure consistent multilingual responses:

```python
# Document RAG Multilingual Prompting
prompt = """
You are a helpful business analyst assistant with access to company documents.
IMPORTANT: You MUST respond in the SAME LANGUAGE as the user's question.
If the user asks in Thai, respond in Thai. If in English, respond in English.
If in any other language, respond in that same language.

User Question: {question}

Instructions:
- Answer based ONLY on the provided document content
- RESPOND IN THE SAME LANGUAGE as the user's question
- Maintain professional tone while matching the user's language
- Provide specific quotes or references from documents when possible
"""
```

#### **Multilingual Implementation Benefits:**

✅ **Enhanced User Experience**: Users can interact in their preferred language  
✅ **Global Accessibility**: Supports international teams and diverse workforces  
✅ **Cultural Sensitivity**: Maintains appropriate tone and context for different languages  
✅ **Consistent Quality**: Same high-quality responses regardless of input language  
✅ **Business Intelligence**: Document search and analytics work seamlessly in any language  

### Technical Implementation

The multilingual system leverages:
- **voyage-multilingual-2 embeddings**: Optimized for cross-language semantic understanding
- **Claude-3.5-Sonnet**: Advanced language model with superior multilingual capabilities
- **Intelligent prompt design**: Language-aware prompting across all response pathways
- **Consistent fallback handling**: Multilingual support even for edge cases and error scenarios

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

## 📈 Current Status & Development Roadmap

### ✅ Completed Features

#### Core Functionality
- ✅ **Advanced RAG Architecture**: Custom vectorization with voyage-multilingual-2 (1024D embeddings)
- ✅ **Intelligent Question Routing**: Automatic classification for math, general knowledge, and document queries
- ✅ **Advanced Multilingual Intelligence**: Automatic language detection with response matching across all query types
- ✅ **Enhanced Prompting System**: Sophisticated prompt engineering for consistent, high-quality multilingual responses
- ✅ **Slack Bot Integration**: Socket Mode with rich message formatting and file uploads
- ✅ **Enterprise Security**: JWT authentication with RSA key pairs and automatic token renewal
- ✅ **Document Processing**: PDF parsing, chunking, and vectorization pipeline
- ✅ **Smart Similarity Filtering**: 0.3 threshold with graceful fallback mechanisms
- ✅ **Consistent LLM Usage**: Claude-3.5-Sonnet across all response types
- ✅ **Performance Optimization**: Token management and efficient vector operations

#### User Experience
- ✅ **Multi-Modal Responses**: Text, data tables, charts, and citations
- ✅ **Chart Generation**: Automatic pie chart creation with Slack file upload
- ✅ **Error Handling**: Comprehensive exception handling with user-friendly messages
- ✅ **Real-Time Processing**: Live chat responses with processing indicators

### 🚀 Priority Development Areas

#### **1. Infrastructure & Deployment (High Priority)**
- [ ] **Complete Production Setup**
  - [ ] Finalize PDF document upload to Snowflake stages
  - [ ] Verify semantic model configuration and testing
  - [ ] Production environment variable validation
  - [ ] End-to-end system testing with real data

- [ ] **Performance Monitoring**
  - [ ] Response time tracking and optimization
  - [ ] Token usage monitoring and cost analysis
  - [ ] Error rate tracking and alerting
  - [ ] Vector search performance metrics

#### **2. Feature Enhancements (Medium Priority)**
- [ ] **Expanded Visualization Support**
  - [ ] Bar charts, line graphs, and scatter plots
  - [ ] Multi-series data visualization
  - [ ] Interactive chart options
  - [ ] Chart type recommendation engine

- [ ] **Advanced Analytics**
  - [ ] Multi-step query processing
  - [ ] Complex aggregations and calculations
  - [ ] Trend analysis and forecasting
  - [ ] Comparative analytics across time periods

#### **3. User Experience Improvements (Medium Priority)**
- [ ] **Conversation Memory**
  - [ ] Context awareness across message sessions
  - [ ] Follow-up question handling
  - [ ] Previous query reference capabilities
  - [ ] Session state management

- [ ] **Enhanced Interaction**
  - [ ] Interactive buttons and menus in Slack
  - [ ] Query suggestion and auto-completion
  - [ ] User preference learning
  - [ ] Feedback collection and processing

#### **4. Advanced Intelligence (Future)**
- [ ] **Dynamic Learning**
  - [ ] Adaptive similarity threshold tuning
  - [ ] User feedback integration for model improvement
  - [ ] Query pattern analysis and optimization
  - [ ] Custom embedding fine-tuning

- [ ] **Multi-Source Integration**
  - [ ] Additional document formats (Word, Excel, PowerPoint)
  - [ ] Database table integration beyond semantic model
  - [ ] Real-time data source connections
  - [ ] External API integration capabilities

## � Quick Start Guide

### Prerequisites
- ✅ Snowflake account with Cortex AI features enabled
- ✅ Slack workspace with bot application created
- ✅ Python 3.8+ environment
- ✅ PDF documents for RAG (stored in `data/` folder)

### 1. Environment Setup
```bash
# Clone the repository
git clone <your-repository-url>
cd Snowflake_CortexAgentRAG_SlackChat

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Snowflake and Slack credentials
```

### 2. Snowflake Infrastructure Setup
```bash
# Execute SQL setup files in order:
# 1. Run setup.sql in Snowflake SQL worksheet
# 2. Upload PDFs to @DASH_DB.DASH_SCHEMA.DASH_PDFS stage
# 3. Upload semantic model to @DASH_DB.DASH_SCHEMA.DASH_SEMANTIC_MODELS stage  
# 4. Run cortex_search_service.sql to create vector search service
```

### 3. Configuration & Testing
```bash
# Test Snowflake connection
python test.py

# Verify Slack bot tokens
# Check SLACK_APP_TOKEN and SLACK_BOT_TOKEN in .env

# Run the application
python app.py
```

### 4. Required Environment Variables
```env
# Snowflake Configuration
ACCOUNT=your_account_identifier
HOST=your_account.snowflakecomputing.com
DEMO_USER=your_username
DEMO_USER_ROLE=ACCOUNTADMIN
DEMO_DATABASE=DASH_DB
DEMO_SCHEMA=DASH_SCHEMA
WAREHOUSE=DASH_S

# Slack Configuration  
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Cortex AI Configuration
AGENT_ENDPOINT=https://your_account.snowflakecomputing.com/api/v2/cortex/agent:run
SEMANTIC_MODEL=@DASH_DB.DASH_SCHEMA.DASH_SEMANTIC_MODELS/support_tickets_semantic_model.yaml
SEARCH_SERVICE=DASH_DB.DASH_SCHEMA.vehicles_info
MODEL=claude-3-5-sonnet

# Security
RSA_PRIVATE_KEY_PATH=rsa_key.p8
```

## 📁 Project Structure

```
Snowflake_CortexAgentRAG_SlackChat/
├── 📄 app.py                                    # Main Slack bot application with RAG logic
├── 📄 cortex_chat.py                           # Cortex Agent API client and communication
├── 📄 generate_jwt.py                          # JWT token generation for authentication
├── 📄 test.py                                  # Connection and API testing utilities
├── 📄 cleanup_files.py                         # File cleanup utilities
├── 📄 requirements.txt                         # Python dependencies
├── 📄 support_tickets_semantic_model.yaml     # Semantic model for data analytics
├── 📄 .env                                     # Environment variables (create from template)
├── 🔐 rsa_key.p8                              # RSA private key for JWT authentication
├── 🔐 rsa_key.pub                             # RSA public key
├── 📄 slack_bot.sh                            # Deployment script for bot
├── 📊 pie_chart.jpg                           # Sample chart output
├── 📄 README.md                               # This documentation
├── 📄 LICENSE                                 # Project license
├── 
├── 📂 data/                                   # PDF documents for RAG
│   ├── City_Motors_Dealership_Contract.pdf
│   ├── DataTires_Contract_Detailed.pdf  
│   ├── Metro_Auto_Dealership_Contract.pdf
│   ├── RubberWorks_Contract_Detailed.pdf
│   ├── Snowtires_Automotive_Contract_with_Appendix.pdf
│   └── Snowtires_Automotive_ESG_Recycling_Policy_Full.pdf
│
├── 📂 snowflake_cortexai_sql/                # Snowflake setup and configuration
│   ├── setup.sql                             # Database and schema creation
│   ├── cortex_search_service.sql             # Vector search service setup
│   ├── check_embedding_dimensions.sql        # Embedding validation queries
│   └── README.md                             # SQL setup instructions
│
├── 📂 snowflake_cleanup_oldfiles/            # Maintenance utilities
│   ├── cleanup_old_files.sql                # File cleanup procedures
│   ├── quick_check_orphaned_files.sql       # Orphaned file detection
│   └── README.md                             # Cleanup documentation
│
└── 📂 __pycache__/                           # Python bytecode cache
    ├── cortex_chat.cpython-312.pyc
    └── generate_jwt.cpython-312.pyc
```

## 💬 Usage Examples & Testing

### 1. Mathematical & Computational Queries (Multilingual)

**English:**
```
User: "What is 2+2?"
Bot: "4"

User: "Calculate 15 * 8"  
Bot: "120"

User: "Solve 144 / 12"
Bot: "12"
```

**Thai:**
```
User: "5+3 เท่ากับเท่าไร?"
Bot: "5+3 เท่ากับ 8"

User: "คำนวณ 12 × 4"
Bot: "12 × 4 เท่ากับ 48"
```

**Spanish:**
```
User: "¿Cuánto es 10 × 7?"
Bot: "10 × 7 es igual a 70"
```

### 2. General Knowledge Questions (Multilingual)

**English:**
```
User: "What is the capital of France?"
Bot: "Paris"

User: "Who invented the telephone?"
Bot: "Alexander Graham Bell invented the telephone in 1876..."
```

**Thai:**
```
User: "เมืองหลวงของประเทศญี่ปุ่นคือที่ไหน?"
Bot: "เมืองหลวงของประเทศญี่ปุ่นคือ โตเกียว (Tokyo)"
```

**Spanish:**
```
User: "¿Quién inventó la bombilla eléctrica?"
Bot: "Thomas Edison inventó la bombilla eléctrica en 1879..."
```
User: "Explain machine learning"
Bot: "Machine learning is a subset of artificial intelligence..."
```

### 3. Document-Specific RAG Queries (Multilingual)

**English:**
```
User: "What are the terms in the DataTires contract?"
Bot: [Searches PDF documents, returns relevant contract sections with citations]

User: "Summarize the ESG policy from Snowtires Automotive"
Bot: [Vector search results with document excerpts and source citations]
```

**Thai:**
```
User: "บริษัทเรามีสัญญากับ DataTires ไหม?"
Bot: [ค้นหาเอกสาร PDF และตอบกลับเป็นภาษาไทยพร้อมอ้างอิง]

User: "สรุปนโยบาย ESG ของ Snowtires Automotive"
Bot: [ผลการค้นหาเวกเตอร์เป็นภาษาไทยพร้อมเนื้อหาและแหล่งอ้างอิง]
```

**Spanish:**
```
User: "¿Cuáles son los términos del contrato con DataTires?"
Bot: [Búsqueda en documentos PDF, devuelve secciones relevantes del contrato con citas]
```

### 4. Data Analytics & SQL Generation (Multilingual)

**English:**
```
User: "Show me a breakdown of support tickets by service type"
Bot: [Generates SQL query, executes it, returns table + pie chart]

User: "How many customers prefer email contact?"
Bot: [SQL analysis with numerical results and visualization]
```

**Thai:**
```
User: "แสดงการแบ่งตั๋วการสนับสนุนตามประเภทบริการ"
Bot: [สร้าง SQL query ดำเนินการ และส่งกลับตารางข้อมูล + กราฟวงกลม]

User: "ลูกค้ากี่คนที่ชอบติดต่อทางอีเมล?"
Bot: [การวิเคราะห์ SQL พร้อมผลลัพธ์เชิงตัวเลขและการแสดงผล]
```

**Spanish:**
```
User: "Muéstrame un desglose de tickets de soporte por tipo de servicio"
Bot: [Genera consulta SQL, la ejecuta, devuelve tabla + gráfico circular]
```

### 5. Smart Question Routing Examples (Multilingual)

**English:**
```
User: "Tell me about Python programming"
Response: General knowledge (low similarity to business documents)

User: "What are our payment terms with suppliers?"
Response: Document search (high similarity to contract PDFs)

User: "Show customer satisfaction metrics"
Response: SQL generation (matches semantic model dimensions)
```

**Thai:**
```
User: "บอกเกี่ยวกับการเขียนโปรแกรม Python"
Response: ความรู้ทั่วไป (ความคล้ายคลึงต่ำกับเอกสารธุรกิจ)

User: "เงื่อนไขการชำระเงินกับซัพพลายเออร์ของเราคืออะไร?"
Response: การค้นหาเอกสาร (ความคล้ายคลึงสูงกับ PDF สัญญา)

User: "แสดงเมตริกความพึงพอใจของลูกค้า"
Response: การสร้าง SQL (ตรงกับมิติของโมเดลเชิงความหมาย)
```

## 🔧 Technical Implementation Details

### Enhanced Vector Search Pipeline

#### Embedding Model: voyage-multilingual-2
- **Dimensions**: 1024 (high-quality semantic representation)
- **Provider**: Snowflake Cortex (`SNOWFLAKE.CORTEX.EMBED_TEXT_1024`)
- **Type**: Multilingual embedding optimized for retrieval tasks
- **Implementation**: Custom vectorization in `vectorize_answer()` function

#### Intelligent Question Classification
```python
def is_general_question(question):
    """Automatic classification logic"""
    # Mathematical patterns: "2+2", "calculate 10*5", "solve 15/3"
    # General knowledge: "capital of France", "who invented...", "define..."
    # Business queries: High similarity (≥0.3) to document vectors
    # Fallback: Low similarity (<0.3) → General knowledge mode
```

#### Vector Similarity Processing
```python
# Custom vectorization with voyage-multilingual-2
vector_search.with_column('EMBEDQ', 
    F.call_function('SNOWFLAKE.CORTEX.EMBED_TEXT_1024', 
                   F.lit('voyage-multilingual-2'), 
                   F.col('QUESTION')))

# Similarity threshold with smart fallback
if top_similarity < 0.3:
    return direct_llm_response(question)  # General knowledge
else:
    return rag_response_with_citations(question)  # Document search
```

### Performance Optimizations

#### Token Management Strategy
- **Document Chunks**: 5,000 characters per document (prevents token overflow)
- **Context Window**: Optimized for Claude-3.5-Sonnet limits  
- **Aggregation**: Smart text concatenation with proper formatting
- **Graceful Degradation**: Automatic fallback handling for large documents

#### Caching & Efficiency
- **Embedding Caching**: `.cache_result()` for repeated vector operations
- **Session Management**: Persistent Snowflake connections
- **Memory Optimization**: Efficient DataFrame operations with Snowpark

### Security & Authentication

#### JWT Implementation
```python
# RSA-based JWT with automatic renewal
jwt_generator = JWTGenerator(account, user, private_key_path)
token = jwt_generator.get_token()

# Secure API communication
headers = {
    'X-Snowflake-Authorization-Token-Type': 'KEYPAIR_JWT',
    'Authorization': f'Bearer {token}'
}
```

#### Data Privacy
- **Encrypted Communication**: All API calls use HTTPS/TLS
- **Key Management**: RSA private keys for authentication  
- **Access Control**: Role-based permissions in Snowflake
- **Token Expiration**: Automatic JWT renewal handling

## 🧪 Testing & Validation

### Automated Testing Suite
```bash
# Primary connection test
python test.py

# Component validation
python -c "from cortex_chat import CortexChat; print('✅ Cortex Chat import successful')"
python -c "from generate_jwt import JWTGenerator; print('✅ JWT Generator import successful')"

# Environment validation
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ Environment loaded')"
```

### Manual Testing Checklist

#### **1. Question Routing Validation (Multilingual)**

**English Tests:**
```bash
# Mathematical queries (should bypass document search)
Test: "What is 5 + 3?"
Expected: Direct response "8"

Test: "Calculate 144 / 12"  
Expected: Direct response "12"

# General knowledge (should bypass document search)
Test: "What is the capital of Japan?"
Expected: Direct response "Tokyo"
```

**Thai Tests:**
```bash
# Mathematical queries
Test: "5+3 เท่ากับเท่าไร?"
Expected: Direct Thai response "5+3 เท่ากับ 8"

Test: "คำนวณ 144 ÷ 12"
Expected: Direct Thai response "144 ÷ 12 เท่ากับ 12"

# General knowledge
Test: "เมืองหลวงของประเทศไทยคือที่ไหน?"
Expected: Direct Thai response "เมืองหลวงของประเทศไทยคือ กรุงเทพมหานคร"
```

**Spanish Tests:**
```bash
# Mathematical queries
Test: "¿Cuánto es 10 × 7?"
Expected: Direct Spanish response "10 × 7 es igual a 70"

# General knowledge
Test: "¿Cuál es la capital de España?"
Expected: Direct Spanish response "La capital de España es Madrid"
```

#### **2. Document RAG Testing (Multilingual)**

**English Tests:**
```bash
# Business document queries (should search PDFs)
Test: "What are our contract terms with DataTires?"
Expected: PDF content with citations in English

Test: "Summarize the ESG recycling policy"
Expected: Policy excerpts with document sources in English
```

**Thai Tests:**
```bash
# Business document queries
Test: "บริษัทเรามีสัญญากับ DataTires ไหม?"
Expected: PDF content with citations in Thai

Test: "สรุปนโยบาย ESG เกี่ยวกับการรีไซเคิล"
Expected: Policy excerpts with document sources in Thai
```

**Fallback Testing:**
```bash
# Similarity threshold testing (any language)
Test: "Explain quantum computing principles" (English)
Expected: Fallback to general knowledge in English

Test: "อธิบายหลักการคอมพิวเตอร์ควอนตัม" (Thai)
Expected: Fallback to general knowledge in Thai
```

#### **3. Data Analytics Validation**
```bash
# SQL generation and visualization
Test: "Show me support ticket breakdown by service type"
Expected: SQL execution + data table + pie chart

Test: "How many customers prefer email contact?"
Expected: Numerical analysis with potential visualization
```

### Performance Benchmarks

#### **Response Time Targets**
- Mathematical queries: < 2 seconds
- General knowledge: < 3 seconds  
- Document RAG: < 5 seconds
- Data analytics with charts: < 8 seconds

#### **Quality Metrics**
- Vector similarity relevance: ≥ 0.3 for document matches
- Citation accuracy: 100% (all document responses include sources)
- Chart generation success: > 90% for suitable data
- Error handling: Graceful degradation for all failure modes

### Debug Mode
```python
# Enable debugging in cortex_chat.py
DEBUG = True

# Enable debugging in app.py  
DEBUG = True

# Check detailed logs for:
# - JWT token generation and renewal
# - Vector similarity scores  
# - API response parsing
# - Slack file upload processes
```

## 🎉 Success Metrics & Validation

### System Health Indicators
**You'll know the system is working correctly when:**

- ✅ **Smart Routing**: Math questions like "2+2" return "4" instantly without searching documents
- ✅ **General Knowledge**: Questions like "What is the capital of France?" return "Paris" directly  
- ✅ **Document Search**: Business queries return relevant PDF content with proper citations
- ✅ **Similarity Filtering**: Unrelated questions gracefully fall back to general knowledge mode
- ✅ **No Token Errors**: System handles large documents without "max tokens exceeded" errors
- ✅ **Consistent Quality**: All responses use Claude-3.5-Sonnet for consistent, high-quality output
- ✅ **Slack Integration**: Rich message formatting with charts and comprehensive error handling
- ✅ **Performance**: Fast responses due to intelligent routing and optimized token usage

### Comprehensive Testing Matrix (Multilingual)

**English Intelligence:**
```bash
# Mathematical Intelligence
"What is 15 × 7?"                    → Expected: "105"
"Calculate 256 ÷ 16"                 → Expected: "16"

# General Knowledge Validation  
"What is the capital of Australia?"  → Expected: "Canberra"
"Who wrote Romeo and Juliet?"        → Expected: "William Shakespeare"

# Document RAG Verification
"What are our contract terms?"       → Expected: PDF content + citations
"Summarize our ESG policies"         → Expected: Policy excerpts + sources
```

**Thai Intelligence:**
```bash
# Mathematical Intelligence
"15 × 7 เท่ากับเท่าไร?"              → Expected: "15 × 7 เท่ากับ 105"
"คำนวณ 256 ÷ 16"                    → Expected: "256 ÷ 16 เท่ากับ 16"

# General Knowledge Validation
"เมืองหลวงของออสเตรเลียคือที่ไหน?"    → Expected: "เมืองหลวงของออสเตรเลียคือ แคนเบอร์รา"
"ใครเขียน Romeo and Juliet?"       → Expected: "วิลเลียม เชกสเปียร์เขียน Romeo and Juliet"

# Document RAG Verification  
"เงื่อนไขสัญญาของเราคืออะไร?"         → Expected: เนื้อหา PDF + การอ้างอิงเป็นภาษาไทย
"สรุปนโยบาย ESG ของเรา"            → Expected: ข้อความจากนโยบาย + แหล่งอ้างอิงเป็นภาษาไทย
```

**Spanish Intelligence:**
```bash
# Mathematical Intelligence
"¿Cuánto es 15 × 7?"                → Expected: "15 × 7 es igual a 105"
"Calcula 256 ÷ 16"                  → Expected: "256 ÷ 16 es igual a 16"

# General Knowledge Validation
"¿Cuál es la capital de Australia?"  → Expected: "La capital de Australia es Canberra"
"¿Quién escribió Romeo y Julieta?"   → Expected: "William Shakespeare escribió Romeo y Julieta"
```

## 📚 Resources & Documentation

### Official Documentation
- 📖 [Snowflake Cortex AI Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- 🤖 [Slack Bolt Python Framework](https://slack.dev/bolt-python/tutorial/getting-started)
- 🚀 [Original Snowflake QuickStart Guide](https://quickstarts.snowflake.com/guide/integrate_snowflake_cortex_agents_with_slack/index.html)
- 🔧 [Snowpark Python Developer Guide](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)

### Additional Learning Resources
- 🎯 [Vector Embeddings in Snowflake](https://docs.snowflake.com/en/user-guide/snowflake-cortex/vector-functions)
- 📊 [Cortex Analyst for SQL Generation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- 🔐 [JWT Authentication with Snowflake](https://docs.snowflake.com/en/developer-guide/sql-api/authenticating)

## 🤝 Contributing & Development

### Contribution Guidelines
1. **Fork the repository** and create a feature branch
2. **Follow existing code patterns** and documentation standards
3. **Test thoroughly** using the provided testing checklist
4. **Update documentation** for any new features or changes
5. **Submit a pull request** with detailed description of changes

### Development Best Practices
- Use type hints in Python code
- Follow PEP 8 style guidelines
- Add comprehensive error handling
- Include docstrings for all functions
- Test both success and failure scenarios

### Common Issues & Solutions
```bash
# JWT Token Issues
Solution: Verify RSA key format and account identifier

# Vector Search Performance
Solution: Check embedding dimensions and similarity thresholds

# Slack File Upload Failures  
Solution: Verify bot permissions and file size limits

# SQL Generation Errors
Solution: Validate semantic model configuration
```

## 📄 License & Acknowledgments

### License Information
This project is part of **Snowflake Labs** and follows the associated licensing terms. Please refer to the LICENSE file for complete details.

### Acknowledgments
- **Snowflake Labs** for the foundational QuickStart guide and Cortex AI platform
- **Slack** for the robust Bolt framework and API ecosystem
- **Anthropic** for the Claude-3.5-Sonnet language model
- **Contributors** who have helped improve and extend this project

### Project Maintainers
For questions, issues, or contributions, please refer to the repository's issue tracker and contribution guidelines.

---

**⭐ Star this repository if you find it helpful!**

**🚀 Ready to build intelligent conversational AI with Snowflake and Slack? Get started with the Quick Start Guide above!**
