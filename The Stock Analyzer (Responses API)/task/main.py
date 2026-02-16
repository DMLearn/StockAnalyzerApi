import os
import requests
from openai import OpenAI, OpenAIError, AuthenticationError, APIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

system_promt = """You are a helpful financial agent with access to market data through Alpha Vantage MCP Server.
IMPORTANT: Alpha Vantage functions are accessed via wrapper tools:
  - Use TOOL_LIST to see available functions (TIME_SERIES_DAILY, RSI, COMPANY_OVERVIEW, etc.)
  - Use TOOL_CALL with the format: TOOL_CALL(tool_name="FUNCTION_NAME", arguments={...})
  - Example: TOOL_CALL(tool_name="TIME_SERIES_DAILY", arguments={"symbol": "AAPL", "outputsize": "compact"})"""

def get_stock_data(symbol: str, api_key: str):
    """Fetch stock data from Alpha Vantage API"""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            return f"Error: {data['Error Message']}"

        if "Note" in data:
            return "Error: API rate limit reached. Please wait and try again."

        # Extract last 3 days of data
        time_series = data.get("Time Series (Daily)", {})
        recent_days = list(time_series.items())[:3]

        result = f"Stock data for {symbol}:\n\n"
        for date, values in recent_days:
            result += f"Date: {date}\n"
            result += f"  Open: ${values['1. open']}\n"
            result += f"  High: ${values['2. high']}\n"
            result += f"  Low: ${values['3. low']}\n"
            result += f"  Close: ${values['4. close']}\n"
            result += f"  Volume: {values['5. volume']}\n\n"

        return result
    except Exception as e:
        return f"Error fetching stock data: {str(e)}"


def call_openai():
    """Call OpenAI API with prompts"""

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

    print(f"✓ AlphaVantage API Key gefunden")

    try:
        # Fetch stock data from Alpha Vantage
        print("\n→ Lade Aktiendaten von Alpha Vantage...")
        stock_data = get_stock_data("AAPL", alphavantage_api_key)
        print(stock_data)

        # Initialize OpenAI client
        print("→ Initialisiere OpenAI Client...")
        client = OpenAI(api_key=openai_api_key)

        # Create prompt with actual stock data
        user_prompt = f"""Analysiere die folgenden Aktiendaten für AAPL:

{stock_data}

Bitte erstelle eine kurze Zusammenfassung mit:
- Preisbewegung (aufwärts/abwärts/seitwärts)
- Prozentuale Veränderung Tag-zu-Tag
- Auffällige Volumenänderungen"""

        messages = [
            {"role": "system", "content": "Du bist ein hilfreicher Finanzanalyst mit Expertise in Aktienbewertung."},
            {"role": "user", "content": user_prompt}
        ]

        print("→ Sende Anfrage an OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

        print("\n✓ Analyse von OpenAI:\n")
        print(response.choices[0].message.content)

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
    