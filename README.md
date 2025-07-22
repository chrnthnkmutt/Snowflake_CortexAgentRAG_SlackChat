# 🚀 Snowflake Cortex Agents Slack RAG Project

## 📋 Overview

This project implements a sophisticated **Retrieval-Augmented Generation (RAG)** system using Snowflake Cortex Agents integrated with Slack. It combines intelligent question routing, vector similarity search, **enhanced analytical processing**, and automatic visualization to provide AI-powered interactions through a conversational interface.

**✨ NEW: Enhanced Analytical Capabilities** - The system now provides **calculated answers and insights** rather than just document citations, with automatic chart generation for analytical queries.

**Recommend reading the step-by-step project guide here: [Original QuickStart Guide](https://quickstarts.snowflake.com/guide/integrate_snowflake_cortex_agents_with_slack/index.html)**

**Key Features:**
- 🧠 **Intelligent Question Routing**: Automatically detects general knowledge vs document-specific questions
- 🔍 **Document Search (RAG)**: Query PDF documents using vector similarity search with 1024-dimensional embeddings
- 📊 **Enhanced Data Analytics**: Generate SQL queries and intelligent visualizations from natural language
- 🧮 **Analytical Processing**: Calculates specific numbers, percentages, and insights rather than just citing documents
- � **Smart Chart Generation**: Automatically selects optimal chart types (pie, bar, grouped bar) based on data characteristics
- �💬 **Slack Integration**: Conversational AI interface with rich message formatting
- 🎯 **Chart Recommendation**: AI detects when visualizations would be helpful and suggests appropriate chart types
- 🔐 **Secure Authentication**: JWT-based authentication with automatic token renewal
- ⚡ **Hybrid Intelligence**: Seamlessly switches between document-based and general knowledge responses

## 🏗️ Architecture

### Enhanced RAG + Analytics Pipeline
```
Question → Query Enhancement → Analytical System Prompt → [General Knowledge: Direct LLM] OR [Document-Specific: PDF Documents → voyage-multilingual-2 → 1024D Vectors → Similarity Search (>0.25) → Retrieved Context → Enhanced Analytical LLM Generation] → Smart Chart Detection → Automatic Visualization
```

### Components
- **Embedding Model**: `voyage-multilingual-2` (1024 dimensions)
- **LLM**: Claude-3.5-Sonnet (enhanced with analytical prompts)
- **Vector Database**: Snowflake Cortex Search Service with custom vectorization
- **Text Processing**: 1800-character chunks with 300-character overlap  
- **Enhanced Analytics**: Query enhancement for analytical intent detection
- **Smart Chart Generation**: Automatic chart type selection based on data characteristics
- **Intelligent Routing**: Pattern-based detection for math, general knowledge, and document queries
- **Similarity Threshold**: 0.25 minimum for document relevance (improved from 0.3)
- **Interface**: Slack Bot with Socket Mode and rich visualizations

## 🧠 Embedding Model Details

### Current Model: voyage-multilingual-2
- **Provider**: Snowflake Cortex (`SNOWFLAKE.CORTEX.EMBED_TEXT_1024`)
- **Dimensions**: 1024 (high-quality embedding space)
- **Type**: Multilingual embedding model optimized for retrieval
- **Usage**: Custom implementation in `vectorize_answer()` function
- **Performance**: Superior semantic understanding with larger vector space

### Key Implementation Features

#### **✨ NEW: Enhanced Analytical Processing**
The system now provides **calculated insights and analysis** rather than basic document citations:

1. **Analytical Query Enhancement**: Automatically detects analytical intent and enhances queries with specific calculation instructions
2. **Smart System Prompts**: AI is instructed to calculate numbers, percentages, and provide insights
3. **Chart Recommendation**: AI automatically suggests appropriate visualizations for analytical data
4. **Intelligent Chart Generation**: System selects optimal chart types based on data characteristics:
   - **Pie Charts**: For percentage data or small datasets (≤6 items, sum ≤100)
   - **Bar Charts**: For larger numerical data with categories  
   - **Grouped Bar Charts**: For multiple numerical columns
5. **Business Question Detection**: Enhanced pattern matching for business-specific analytical queries

#### **🎯 Analytical Response Examples**
**Before Enhancement**: *"The documents mention cellular and business internet services."*

**After Enhancement**: *"Support ticket analysis shows: Cellular Service: 45 tickets (45%), Business Internet: 30 tickets (30%), Home Internet: 25 tickets (25%). Cellular service generates the highest volume, suggesting potential service quality issues requiring attention. [Pie chart automatically generated]"*

#### **Intelligent Question Routing**
The system automatically categorizes questions and routes them appropriately:

1. **Mathematical Queries**: `"2+2"`, `"calculate 10*5"` → Direct LLM response
2. **General Knowledge**: `"What is the capital of France?"` → Direct LLM response  
3. **Analytical Business Queries**: `"breakdown of support tickets"` → Enhanced analytical processing with calculations
4. **Document-Specific**: High similarity to documents → RAG pipeline with enhanced analytical prompts
5. **Low Similarity**: Questions with <0.25 similarity to documents → Fallback to general knowledge

#### **Enhanced Vector Similarity Processing**
```python
# Custom vectorization with voyage-multilingual-2 (1024D)
vector_search.with_column('EMBEDQ', F.call_function('SNOWFLAKE.CORTEX.EMBED_TEXT_1024', 
                                                   F.lit('voyage-multilingual-2'), 
                                                   F.col('QUESTION')))

# Improved similarity threshold filtering (lowered from 0.3 to 0.25)
if top_similarity < 0.25:  # Smart fallback to general knowledge
    return enhanced_analytical_response(question)

# Enhanced analytical prompting for document-based queries
analytical_prompt = f"""
Question: {question}

You are an analytical AI assistant. For this question:
1. If it asks for breakdowns, comparisons, or calculations, provide specific numbers and percentages
2. If it asks for visual representation, recommend appropriate visualization
3. Analyze patterns and provide insights, not just raw information
4. Calculate derived metrics when possible (percentages, ratios, trends)

Based on the following document content, analyze and calculate the answer:
"""
```

#### **Smart Chart Generation Logic**
```python
# Automatic chart type selection based on data characteristics
if len(categorical_cols) == 1 and len(numerical_cols) == 1:
    if data_sum <= 100 or len(data) <= 6:
        chart_type = "Pie Chart"  # Perfect for percentages
    else:
        chart_type = "Bar Chart"  # Better for larger numbers
elif len(numerical_cols) >= 2:
    chart_type = "Grouped Bar Chart"  # Multiple metrics comparison
```

#### **Token Optimization**
- **Document Chunks**: Limited to 6,000 characters per document (increased from 5,000 for better context)
- **Context Window**: Optimized prompting to stay within Claude-3.5-Sonnet's limits
- **Efficient Aggregation**: Smart text concatenation with analytical formatting
- **Enhanced Context**: Increased similarity search results (5 vs 3) for better analytical context

## 🎯 Current Status & Next Steps

### ✅ **Completed**
- ✅ **Enhanced RAG Architecture**: Custom vectorization with voyage-multilingual-2 (1024D)
- ✅ **Intelligent Question Routing**: Automatic detection of general vs document-specific queries
- ✅ **🆕 Enhanced Analytical Processing**: AI now calculates and analyzes rather than just citing
- ✅ **🆕 Smart Chart Generation**: Automatic chart type selection (pie, bar, grouped bar)
- ✅ **🆕 Chart Recommendation Detection**: AI suggests visualizations when appropriate
- ✅ **🆕 Query Enhancement**: Analytical intent detection and prompt improvement
- ✅ **Slack Bot Integration**: Socket Mode with rich message formatting
- ✅ **JWT Authentication**: Secure authentication system
- ✅ **PDF Document Processing**: Text chunking and vectorization
- ✅ **Smart Similarity Filtering**: 0.25 threshold for document relevance (improved from 0.3)
- ✅ **Consistent Model Usage**: Claude-3.5-Sonnet across all LLM calls
- ✅ **Token Optimization**: 6K character limits with enhanced context
- ✅ **🆕 Comprehensive Testing**: Test suite for analytical capabilities

### 🚀 **Priority Next Steps**

#### **🔧 1. Setup & Deployment (High Priority)**
- [ ] **Complete environment setup**
  - Upload PDF documents to `@DASH_DB.DASH_SCHEMA.DASH_PDFS` stage
  - Upload semantic model to `@DASH_DB.DASH_SCHEMA.DASH_SEMANTIC_MODELS` stage
  - Run `setup.sql` to create infrastructure
  - Run `cortex_search_service.sql` to build search service with voyage-multilingual-2

- [ ] **🆕 Test enhanced analytical functionality**
  - Run `python test_enhanced_analytics.py` to validate analytical capabilities
  - Test breakdown queries: `"Show me a breakdown of support tickets by service type"` (should calculate percentages and recommend charts)
  - Test chart generation: `"Create a chart of customer service data"` (should auto-generate appropriate visualization)
  - Test analytical comparisons: `"Compare recycling efficiency between methods"` (should provide calculated insights)
  - Verify mathematical queries: `"What is 2+2?"` (should return 4 directly)
  - Verify general knowledge: `"What is the capital of France?"` (should return Paris)
  - Test document queries: `"What are the contract terms?"` (should search PDFs with analytical processing)

#### **🐛 2. Optimize Current Implementation (Medium Priority)**
- [ ] **Fine-tune similarity threshold**: Test 0.2, 0.25, 0.3 thresholds for optimal routing
- [ ] **🆕 Expand analytical patterns**: Add more regex patterns for better analytical question detection
- [ ] **🆕 Chart type optimization**: Fine-tune chart selection logic based on user feedback
- [ ] **Performance optimization**: Cache embeddings for common queries
- [ ] **Error handling**: Improve robustness for edge cases

#### **✨ 3. Feature Enhancements (Medium Priority)**
- [ ] **Conversation Memory**: Add context awareness across messages
- [ ] **🆕 Advanced Chart Types**: Add line charts, scatter plots, heatmaps
- [ ] **🆕 Statistical Analysis**: Implement trend analysis and correlation detection
- [ ] **🆕 Multi-dataset Analytics**: Support combining data from multiple sources
- [ ] **🆕 Interactive Visualizations**: Create clickable, zoomable charts
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

# 5. Test the enhanced analytics
python test_enhanced_analytics.py

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
├── app.py                          # Main Slack bot application (enhanced with smart chart generation)
├── cortex_chat.py                  # Cortex Agents API client (enhanced with analytical prompting)
├── generate_jwt.py                 # JWT token generation
├── setup.sql                       # Snowflake infrastructure setup
├── cortex_search_service.sql       # Search service creation
├── support_tickets_semantic_model.yaml  # Semantic model definition
├── test.py                         # API connection testing
├── test_enhanced_analytics.py      # 🆕 Enhanced analytics testing suite
├── ENHANCED_ANALYTICS_SUMMARY.md   # 🆕 Detailed implementation guide
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── data/                          # PDF documents for RAG
└── README.md                      # This file
```

## 🎮 Enhanced Usage Examples

### 🆕 **Analytical Queries (NEW!)**
```
"Can you show me a breakdown of customer support tickets by service type cellular vs business internet?"
→ Response: "Support ticket analysis shows:
   - Cellular Service: 45 tickets (45%)
   - Business Internet: 30 tickets (30%) 
   - Home Internet: 25 tickets (25%)
   
   Cellular service generates the highest volume, suggesting potential service quality issues.
   [Pie chart automatically generated showing distribution]"

"What percentage of tickets are for cellular service vs business internet?"
→ Response: "Based on the data analysis:
   - Cellular Service: 60% of tickets (45 out of 75 total)
   - Business Internet: 40% of tickets (30 out of 75 total)
   
   This shows a 1.5:1 ratio favoring cellular service issues."

"Create a chart showing the distribution of support tickets by service type"
→ Response: "I'll analyze the support ticket data and create a visualization:
   [SQL query generated] → [Data calculated] → [Pie chart automatically created]
   
   The chart shows cellular service dominates support requests at 45%."

"Compare the recycling efficiency between rubber tires and carbon black"
→ Response: "Recycling efficiency analysis:
   - Rubber recovery: Up to 80% efficiency for tires with >60% rubber content
   - Carbon black recovery: 70% efficiency for tires with >30% carbon black content
   
   Rubber recycling shows 10% higher efficiency rates."
```

### Mathematical & General Knowledge Queries
```
"What is 2+2?"                          → Direct response: "4"
"Calculate 15 * 8"                      → Direct response: "120"
"What is the capital of France?"        → Direct response: "Paris"
"Who invented the telephone?"           → Direct response: Historical information
```

### Document-Specific Queries (Enhanced RAG)
```
"What are the terms in the DataTires contract?"          → Searches PDFs, returns relevant sections with analysis
"Summarize the ESG policy from Snowtires Automotive"    → Vector search + analytical document analysis  
"What recycling procedures are mentioned?"              → PDF content with citations and efficiency calculations
```

### Smart Routing Examples
```
"Tell me about Python programming"       → General knowledge (low similarity to business docs)
"What are our payment terms?"           → Document search with analytical processing (high similarity to contracts)
"Compare machine learning models"       → General knowledge (no relevant business docs)
```

### 🆕 **Enhanced Data Analytics (SQL Generation + Smart Charts)**
```
"Show me a breakdown of support tickets by service type"
→ Generates SQL + Creates appropriate chart (pie chart for categorical breakdown)

"How many customers prefer email contact?"  
→ Calculates percentages + Creates bar chart if multiple contact methods

"Create a chart of customer distribution"
→ Analyzes data structure + Selects optimal visualization type
```

## 🔧 Development

### Key Components

#### **🆕 Enhanced CortexChat Class** (`cortex_chat.py`)
- **Analytical Query Enhancement**: Automatically detects analytical intent and enhances prompts
- **Smart System Prompts**: Instructs AI to calculate rather than just cite documents
- **Chart Recommendation Detection**: Identifies when AI suggests visualizations
- Handles Cortex Agents API communication with enhanced analytical processing
- Manages JWT authentication with automatic renewal
- Processes streaming responses (SSE) with analytical result parsing

#### **🆕 Enhanced Slack Bot** (`app.py`)
- **Smart Chart Generation**: `plot_smart_chart()` function automatically selects optimal chart types
- **Chart Triggering Logic**: Creates visualizations when AI recommends them or data supports it
- **Enhanced Response Display**: Better formatting for analytical results
- Socket Mode integration for real-time messaging
- Rich message formatting with improved chart handling
- Comprehensive error handling and user feedback

#### **🆕 Enhanced Vectorize Answer Function** (`app.py`)
- **Enhanced Analytical Prompting**: Instructs AI to provide calculations and insights
- **Business Question Detection**: Improved pattern matching for analytical business queries
- **Increased Context**: Uses 5 documents instead of 3 for better analytical context
- **Improved Similarity Threshold**: Lowered to 0.25 for better coverage
- Custom Vector Search with voyage-multilingual-2 (1024-dimensional embeddings)
- Token Management with increased context window (6,000 characters)
- Consistent LLM usage with Claude-3.5-Sonnet

#### **Enhanced Vectorize Answer Function** (`app.py`)
- **Intelligent Question Routing**: Automatically detects math, general knowledge, and document queries
- **Custom Vector Search**: Uses voyage-multilingual-2 with 1024-dimensional embeddings
- **Similarity Threshold**: 0.3 minimum for document relevance detection
- **Token Management**: 5,000 character limit per document to prevent overflow
- **Consistent LLM**: Claude-3.5-Sonnet for all text generation

#### **Custom Vector Search** (`cortex_search_service.sql`)
- PDF document parsing and chunking
- **Updated**: Vector embedding with voyage-multilingual-2 (1024D)
- Enhanced similarity search with threshold filtering

### Testing
```bash
# Test enhanced analytical capabilities
python test_enhanced_analytics.py

# Test Cortex Agents API  
python test.py

# Test individual components
python -c "from cortex_chat import CortexChat; print('Import successful')"

# Debug mode
# Set DEBUG = True in cortex_chat.py for detailed logging
```

## 📊 Technical Details

### 🆕 **Enhanced Analytical Implementation**
- **Query Enhancement**: `_enhance_query_for_analysis()` method detects analytical intent
- **Smart Prompting**: Enhanced system prompts for calculation-focused responses
- **Chart Detection**: Automatic identification of visualization opportunities
- **Data Analysis**: Improved document processing with analytical focus

### 🆕 **Smart Chart Generation**
```python
# Automatic chart type selection
if len(categorical_cols) == 1 and len(numerical_cols) == 1:
    if data_sum <= 100 or len(data) <= 6:
        chart_type = "Pie Chart"    # Perfect for percentages/small datasets
    else:
        chart_type = "Bar Chart"    # Better for larger numbers
elif len(numerical_cols) >= 2:
    chart_type = "Grouped Bar Chart"  # Multiple metrics comparison
```

### Enhanced Embedding Implementation
- **Model**: voyage-multilingual-2 (via `SNOWFLAKE.CORTEX.EMBED_TEXT_1024`)
- **Dimensions**: 1024 (upgraded from 768 for better semantic understanding)
- **Implementation**: Custom vectorization in `vectorize_answer()` function
- **Optimization**: High-quality retrieval with multilingual support

### Intelligent Question Classification
```python
# Enhanced business question detection
business_patterns = [
    r'support\s+ticket',             # "support ticket breakdown"  
    r'customer.*service',            # "customer service breakdown"
    r'breakdown.*by',                # "breakdown by service type"
    r'compare.*service',             # "compare services"
    r'cellular.*business',           # "cellular vs business"
    r'percentage.*customers',        # Customer percentage questions
]

# Mathematical patterns: "2+2", "calculate 10*5"
# General knowledge: "capital of France", "who invented..."
# Document-specific: High similarity (>0.25) to PDF content with analytical processing
# Fallback: Low similarity (<0.25) → Enhanced general knowledge mode
```

### 🆕 **Smart Similarity Threshold** 
- **Threshold**: 0.25 cosine similarity minimum (improved from 0.3 for better coverage)
- **Above 0.25**: Uses enhanced RAG pipeline with PDF content, analytical prompts, and citations
- **Below 0.25**: Falls back to enhanced general knowledge mode with analytical processing
- **Benefits**: Better coverage while preventing irrelevant document content

### Token Optimization Strategy
- **Document Chunks**: 6,000 characters per document (increased from 5,000 for better analytical context)
- **Context Window**: Optimized prompting for Claude-3.5-Sonnet with analytical instructions
- **Aggregation**: Smart text concatenation with analytical formatting
- **Fallback**: Automatic token limit handling with graceful degradation
- **Enhanced Context**: 5 document limit (vs 3) for better analytical insights

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

**You'll know the enhanced analytical system is working when:**
- ✅ **🆕 Analytical Responses**: Business questions return calculated insights with specific numbers and percentages
- ✅ **🆕 Smart Chart Generation**: System automatically creates appropriate visualizations (pie, bar, grouped bar charts)
- ✅ **🆕 Chart Recommendations**: AI suggests when visualizations would be helpful
- ✅ **🆕 Enhanced Calculations**: Questions about breakdowns return computed analysis, not just citations
- ✅ **Smart Routing**: Math questions like "2+2" return "4" instantly without searching documents
- ✅ **General Knowledge**: Questions like "What is the capital of France?" return "Paris" directly
- ✅ **Document Search**: Business queries return relevant PDF content with enhanced analytical processing
- ✅ **Similarity Filtering**: Unrelated questions gracefully fall back to enhanced general knowledge mode
- ✅ **No Token Errors**: System handles large documents without "max tokens exceeded" errors
- ✅ **Consistent Quality**: All responses use Claude-3.5-Sonnet for consistent, high-quality output
- ✅ **Slack Integration**: Rich message formatting with automatic charts and error handling
- ✅ **Performance**: Fast responses due to intelligent routing and optimized token usage

### 🆕 **Enhanced Analytics Testing Checklist**
```bash
# Test enhanced analytical capabilities
python test_enhanced_analytics.py

# Test analytical breakdown queries  
"Can you show me a breakdown of customer support tickets by service type cellular vs business internet?"
# Expected: Specific percentages with chart generation

# Test percentage calculations
"What percentage of tickets are for cellular service vs business internet?"  
# Expected: Calculated percentages with ratio analysis

# Test chart generation requests
"Create a chart showing the distribution of support tickets by service type"
# Expected: Appropriate chart type selection with data visualization

# Test analytical comparisons
"Compare the recycling efficiency between rubber tires and carbon black"
# Expected: Calculated efficiency percentages with comparative analysis

# Test mathematical queries
"What is 5 + 3?"                    # Should return: 8

# Test general knowledge  
"What is the capital of Japan?"     # Should return: Tokyo

# Test document-specific queries
"What are our contract terms?"      # Should search PDFs with analytical processing

# Test similarity threshold
"Explain quantum physics"           # Should fall back to enhanced general knowledge

# Test data analytics
"Show support ticket breakdown"     # Should generate SQL and smart charts
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
