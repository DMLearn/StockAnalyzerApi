# Stock Analyzer Demo Project

## Überblick
Dieses Demo-Projekt zeigt die Verwendung der **OpenAI Responses API** in Verbindung mit einem **MCP Server** (Model Context Protocol) zur Analyse von Aktienmarktdaten.

## Was ist ein MCP Server?

**MCP (Model Context Protocol)** ist ein standardisiertes Protokoll, das es LLMs (Large Language Models) ermöglicht, mit externen Datenquellen und APIs zu kommunizieren.

### Kernkonzepte:

1. **Erweiterung von LLM-Fähigkeiten**: Das LLM kann über den MCP Server auf Echtzeit-Daten zugreifen, die nicht in seinen Trainingsdaten enthalten sind

2. **Standardisierte Schnittstelle**: Der MCP Server fungiert als Brücke zwischen dem LLM und externen APIs (hier: Alpha Vantage für Finanzdaten)

3. **Tool-Bereitstellung**: Der MCP Server stellt dem LLM Tools zur Verfügung (z.B. `TIME_SERIES_DAILY` für tägliche Aktienkurse)

4. **Orchestrierung**:
   - Das LLM entscheidet, welche Tools es aufrufen muss
   - Der MCP Server führt die API-Calls aus
   - Das LLM verarbeitet die Ergebnisse und generiert eine Antwort

## Projektstruktur

```
The Stock Analyzer (Responses API)/
└── task/
    └── main.py          # Hauptanwendung
```

## Funktionsweise in diesem Projekt

```python
# 1. MCP Server Konfiguration
response = client.responses.create(
    model="gpt-4",
    tools=[{
        "type": "mcp",
        "server_label": "AlphaVantage",
        "server_url": alphavantage_mcp_server,
        "authorization": alphavantage_api_key,
    }]
)
```

### Wie das LLM die verfügbaren Tools erfährt (Endpoint `tool_list`)

Sobald du im `tools`-Block einen MCP Server angibst, fragt die OpenAI Responses API den MCP Server automatisch nach den verfügbaren Tools ab. Dafür nutzt der MCP Server den standardisierten Endpoint `tool_list`.

Kurzablauf:

1. **Registrierung**: Du übergibst `server_url` + `authorization` in der MCP-Tool-Konfiguration.
2. **Discovery**: Die OpenAI Responses API ruft am MCP Server den Endpoint **`tool_list`** auf.
3. **Tool-Definitionen**: Der MCP Server liefert eine strukturierte Liste zurück (Tool-Namen, Beschreibungen, Input-Schema).
4. **LLM-Context**: Diese Tool-Definitionen werden in den Model-Context aufgenommen, damit das LLM weiß, welche Calls erlaubt sind und welche Parameter erwartet werden.
5. **Tool-Call**: Erst danach kann das LLM einen konkreten Tool-Call wie `TIME_SERIES_DAILY` erzeugen.

Wichtig: Das LLM sieht nur die **Tool-Metadaten** (Name, Beschreibung, Schema), nicht die internen Implementierungen oder geheimen Credentials. Die Authentifizierung bleibt serverseitig beim MCP Server.

### Ablauf:

1. **User Input**: "Analysiere AAPL-Aktie der letzten 3 Tage"
2. **LLM Entscheidung**: GPT-4 erkennt, dass Aktiendaten benötigt werden
3. **MCP Tool Call**: LLM ruft `TIME_SERIES_DAILY` über den MCP Server auf
4. **Datenabfrage**: MCP Server holt Daten von Alpha Vantage API
5. **Antwortgenerierung**: LLM analysiert die Daten und erstellt eine Zusammenfassung

## Voraussetzungen

- Python 3.x
- OpenAI API Key
- Alpha Vantage API Key

## Installation

```bash
# Dependencies installieren
pip install -r requirements.txt

# .env Datei erstellen
echo "OPENAI_API_KEY=your_openai_key" > .env
echo "AUTHORIZATION=your_alphavantage_key" >> .env
echo "SERVER_URL=your_mcp_server_url" >> .env
```

## Ausführung

```bash
python "The Stock Analyzer (Responses API)/task/main.py"
```

## Vorteile des MCP-Ansatzes

✅ **Echtzeit-Daten**: Zugriff auf aktuelle Informationen
✅ **Modularität**: Einfaches Hinzufügen weiterer Datenquellen
✅ **Sicherheit**: API-Keys werden serverseitig verwaltet
✅ **Flexibilität**: LLM wählt automatisch die richtigen Tools
✅ **Standardisierung**: Einheitliches Protokoll für verschiedene APIs

## Beispiel-Output

Das Programm gibt eine detaillierte Analyse der AAPL-Aktie aus, inklusive:
- Preisbewegung (up/down/flat)
- Prozentuale Änderungen
- Volumenänderungen

## Technologien

- **OpenAI Responses API**: LLM-Orchestrierung
- **MCP Protocol**: Tool-Integration
- **Alpha Vantage**: Finanzdaten-API
- **Python**: Programmiersprache
