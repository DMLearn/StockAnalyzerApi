# Stock Analyzer - OpenAI Responses API with MCP Integration

A demonstration project showcasing the **OpenAI Responses API** integrated with a **Model Context Protocol (MCP) Server** for analyzing stock market data.


This project demonstrates how to leverage OpenAI's advanced AI capabilities to analyze stock market data by integrating with external data sources through the Model Context Protocol. The application retrieves real-time financial data from Alpha Vantage and uses OpenAI's code interpreter to perform comprehensive stock analysis and generate visualizations.


**MCP (Model Context Protocol)** is a standardized protocol that enables Large Language Models (LLMs) to communicate with external data sources and APIs.


1. **Extending LLM Capabilities**: The LLM can access real-time data through the MCP Server that is not included in its training data

2. **Standardized Interface**: The MCP Server acts as a bridge between the LLM and external APIs (in this case: Alpha Vantage for financial data)

3. **Tool Provisioning**: The MCP Server provides the LLM with tools (e.g., `TIME_SERIES_DAILY` for daily stock prices)

4. **Orchestration**:
   - The LLM decides which tools to call
   - The MCP Server executes the API calls
   - The LLM processes the results and generates a response


When you specify an MCP Server in the `tools` block, the OpenAI Responses API automatically queries the MCP Server for available tools using the standardized `tool_list` endpoint.

**Workflow:**

1. **Registration**: You provide `server_url` + `authorization` in the MCP tool configuration
2. **Discovery**: The OpenAI Responses API calls the **`tool_list`** endpoint on the MCP Server
3. **Tool Definitions**: The MCP Server returns a structured list (tool names, descriptions, input schema)
4. **LLM Context**: These tool definitions are included in the model context, so the LLM knows which calls are allowed and what parameters are expected
5. **Tool Call**: Only then can the LLM generate a specific tool call like `TIME_SERIES_DAILY`

**Important**: The LLM only sees the **tool metadata** (name, description, schema), not the internal implementations or secret credentials. Authentication remains server-side with the MCP Server.


```
The Stock Analyzer (Responses API)/
└── The Stock Analyzer (Responses API)/
    └── task/
        └── main.py          # Main application
```


```python
# MCP Server Configuration
response = client.responses.create(
    model="gpt-5-mini",
    tools=[{
        "type": "mcp",
        "server_label": "AlphaVantage",
        "server_url": alphavantage_mcp_server,
        "authorization": alphavantage_api_key,
    }]
)
```


1. **User Input**: "Analyze AAPL stock for the last 3 months"
2. **LLM Decision**: GPT-5-mini recognizes that stock data is needed
3. **MCP Tool Call**: LLM calls `TIME_SERIES_MONTHLY` through the MCP Server
4. **Data Retrieval**: MCP Server fetches data from Alpha Vantage API
5. **Analysis**: LLM analyzes the data using code interpreter
6. **Response Generation**: LLM creates visualizations and a comprehensive analysis


- 📈 **Stock Analysis**: Month-over-month price changes, trend identification, volatility calculations
- 📊 **Automated Visualizations**: Price charts (OHLC) and volume charts
- 🔄 **Real-time Data**: Direct integration with Alpha Vantage API
- 🤖 **AI-Powered Insights**: Leverages GPT-5-mini for intelligent analysis
- 💾 **Export Capabilities**: Automatically saves generated visualizations


- Python 3.8+
- OpenAI API Key
- Alpha Vantage API Key
- MCP Server URL (Alpha Vantage MCP Server)


1. **Clone the repository**
```bash
git clone <repository-url>
cd "The Stock Analyzer (Responses API)"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
AUTHORIZATION=your_alphavantage_api_key_here
SERVER_URL=your_mcp_server_url_here
```


- **OpenAI API Key**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Alpha Vantage API Key**: [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)


Run the main script:

```bash
python "The Stock Analyzer (Responses API)/task/main.py"
```

The application will:
1. Validate your API credentials
2. Connect to the OpenAI Responses API
3. Query Alpha Vantage for AAPL stock data
4. Generate analysis and visualizations
5. Save charts to `stock_image.png`


The program generates a detailed analysis of the AAPL stock, including:

- **Price Movement**: Up/down/sideways trend identification
- **Percentage Changes**: Month-over-month price changes
- **Volume Analysis**: Trading volume trends
- **Key Metrics**: Average closing price, volatility indicators
- **Visual Charts**: OHLC price charts and volume charts


The application is organized into well-defined functions for maintainability:

- `validate_environment_variables()`: Validates required API keys and configuration
- `get_analysis_prompt()`: Generates the stock analysis prompt
- `create_api_response()`: Handles OpenAI API communication with MCP integration
- `save_visualizations()`: Extracts and saves generated charts
- `handle_*_error()`: Comprehensive error handling functions
- `call_openai()`: Main orchestration function


✅ **Real-time Data**: Access to current information
✅ **Modularity**: Easy to add additional data sources
✅ **Security**: API keys are managed server-side
✅ **Flexibility**: LLM automatically selects the right tools
✅ **Standardization**: Uniform protocol for different APIs
✅ **Scalability**: Easy to extend with more financial instruments and analysis types


- **OpenAI Responses API**: LLM orchestration and analysis
- **MCP Protocol**: Tool integration and data source connectivity
- **Alpha Vantage**: Financial market data API
- **Python**: Programming language
- **Code Interpreter**: Automated data analysis and visualization


The application includes comprehensive error handling for:

- Authentication errors (invalid API keys)
- API errors (quota exceeded, service issues)
- Network connectivity issues
- Unexpected runtime errors

Each error type provides helpful diagnostic messages and suggested solutions.


Contributions are welcome! Please feel free to submit a Pull Request.


This project is provided as-is for demonstration purposes.


- OpenAI for the Responses API
- Alpha Vantage for financial market data
- MCP Protocol for standardized LLM-API integration

---

**Note**: This is a demonstration project showcasing MCP integration with OpenAI's Responses API. Ensure you comply with all API usage terms and rate limits.
