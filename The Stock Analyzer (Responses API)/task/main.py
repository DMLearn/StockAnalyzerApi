import os
import json
from openai import OpenAI, OpenAIError, AuthenticationError, APIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def call_openai():
    """Call OpenAI Responses API with Alpha Vantage MCP Server"""

    # Check if API key exists
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ FEHLER: OPENAI_API_KEY Umgebungsvariable ist nicht gesetzt!")
        print("   Bitte überprüfen Sie Ihre .env Datei oder Umgebungsvariablen.")
        return

    print(f"✓ OpenAI API Key gefunden (erste 10 Zeichen): {openai_api_key[:10]}...")

    # Check AlphaVantage API key
    alphavantage_api_key = os.getenv("AUTHORIZATION")
    if not alphavantage_api_key:
        print("❌ FEHLER: AUTHORIZATION Umgebungsvariable ist nicht gesetzt!")
        return

    print(f"✓ AlphaVantage API Key gefunden\n")

    try:
        # Initialize OpenAI client
        print("→ Initialisiere OpenAI Client...")
        client = OpenAI(api_key=openai_api_key)

        # User prompt
        user_prompt = """## Stock Analysis: AAPL

### 1. Data Retrieval
**Price data:**
`TOOL_CALL(tool_name="TIME_SERIES_MONTHLY", arguments={"symbol": "AAPL", "outputsize": "compact"})`

**Technical indicators:**
- `TOOL_CALL(tool_name="RSI", arguments={"symbol": "AAPL", "interval": "monthly", "time_period": 14, "series_type": "close"})`
- `TOOL_CALL(tool_name="SMA", arguments={"symbol": "AAPL", "interval": "monthly", "time_period": 20, "series_type": "close"})`
- `TOOL_CALL(tool_name="SMA", arguments={"symbol": "AAPL", "interval": "monthly", "time_period": 50, "series_type": "close"})`
- `TOOL_CALL(tool_name="BBANDS", arguments={"symbol": "AAPL", "interval": "monthly", "time_period": 20, "series_type": "close"})`

### 2. Analysis
Provide investor-friendly assessment of:
- **Trend & momentum**: RSI status, price vs moving averages
- **Signals**: Oversold/overbought, MA crossovers, Bollinger Band position
- **Risk level**: Low/Moderate/High based on volatility

### 3. Recommendation
Clear **buy/hold/sell** with brief reasoning (2-3 sentences).

*Use plain language — no unexplained jargon.*"""

        alphavantage_mcp_server = os.getenv("SERVER_URL")
        print("\n" + "="*80)
        print("🤖 OPENAI RESPONSES API CALL")
        print("="*80)
        print(f"Model: gpt-4")
        print(f"MCP Server: AlphaVantage")
        print(f"MCP URL: {alphavantage_mcp_server}")
        print(f"User Prompt:\n{user_prompt}")
        print("-"*80)

        # Call OpenAI Responses API with MCP server

        response = client.responses.create(
            model="gpt-5-mini",
            tools=[
                {
                    "type": "mcp",
                    "server_label": "AlphaVantage",
                    "server_description": "Alpha Vantage MCP Server for financial market data",
                    "server_url": alphavantage_mcp_server,
                    "authorization": alphavantage_api_key,
                    "require_approval": "never",
                }
            ],
            input=user_prompt,
        )

        print("\n" + "="*80)
        print("📥 OPENAI RESPONSES API - COMPLETE RESPONSE")
        print("="*80)
        print(json.dumps(response.model_dump(), indent=2))
        print("="*80 + "\n")

        print("\n" + "="*80)
        print("📊 FINAL OUTPUT")
        print("="*80)
        print(response.output)
        print("="*80 + "\n")

    except AuthenticationError as e:
        print("\n❌ AUTHENTIFIZIERUNGSFEHLER:")
        print(f"   Der API-Key ist ungültig oder abgelaufen!")
        print(f"   Details: {str(e)}")
        print("\n   Lösungen:")
        print("   1. Überprüfen Sie ob der API-Key korrekt ist")
        print("   2. Generieren Sie einen neuen API-Key auf: https://platform.openai.com/api-keys")
        print("   3. Überprüfen Sie ob Ihr OpenAI Account noch aktiv ist")

    except APIError as e:
        print("\n❌ API-FEHLER:")
        print(f"   Status Code: {e.status_code if hasattr(e, 'status_code') else 'Unbekannt'}")
        print(f"   Details: {str(e)}")
        print("\n   Mögliche Ursachen:")
        print("   - Quota überschritten (keine Credits mehr)")
        print("   - Temporäre Probleme bei OpenAI")
        print("   - Ungültiges Request-Format")

    except OpenAIError as e:
        print("\n❌ OPENAI-FEHLER:")
        print(f"   Details: {str(e)}")
        print("\n   Bitte überprüfen Sie:")
        print("   - API-Key Gültigkeit")
        print("   - Netzwerkverbindung")
        print("   - OpenAI Service Status: https://status.openai.com/")

    except Exception as e:
        print("\n❌ UNERWARTETER FEHLER:")
        print(f"   Typ: {type(e).__name__}")
        print(f"   Details: {str(e)}")
        print("\n   Bitte kontaktieren Sie den Support mit dieser Fehlermeldung.")


if __name__ == '__main__':
    call_openai()
    