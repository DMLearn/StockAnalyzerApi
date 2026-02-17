"""
Stock Analyzer - OpenAI Responses API with MCP Integration

This module demonstrates the use of OpenAI's Responses API in conjunction with
the Model Context Protocol (MCP) server to analyze stock market data from Alpha Vantage.
"""

import os
import json
from typing import Optional
from openai import OpenAI, OpenAIError, AuthenticationError, APIError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
MODEL = "gpt-5-mini"
MCP_SERVER_LABEL = "AlphaVantage"
OUTPUT_IMAGE_PATH = "stock_image.png"


def validate_environment_variables() -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Validate and retrieve required environment variables.

    Returns:
        tuple: (openai_api_key, alphavantage_api_key, server_url) or (None, None, None) if validation fails
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ ERROR: OPENAI_API_KEY environment variable is not set!")
        print("   Please check your .env file or environment variables.")
        return None, None, None

    print(f"✓ OpenAI API Key found (first 10 characters): {openai_api_key[:10]}...")

    alphavantage_api_key = os.getenv("AUTHORIZATION")
    if not alphavantage_api_key:
        print("❌ ERROR: AUTHORIZATION environment variable is not set!")
        print("   Please add your Alpha Vantage API key to the .env file.")
        return None, None, None

    print(f"✓ Alpha Vantage API Key found")

    server_url = os.getenv("SERVER_URL")
    if not server_url:
        print("❌ ERROR: SERVER_URL environment variable is not set!")
        print("   Please add your MCP server URL to the .env file.")
        return None, None, None

    print(f"✓ MCP Server URL found\n")

    return openai_api_key, alphavantage_api_key, server_url

def get_analysis_prompt() -> str:
    """
    Generate the stock analysis prompt for the AI model.

    Returns:
        str: Formatted prompt with analysis requirements
    """
    return """Please analyze the Apple stock (AAPL) for the last 3 months using monthly data
    as the time window and not the daily prices.
    Use AlphaVantage as the data source for stock prices and the Code_interpreter tool for analysis.

    ### Analysis
    - Calculate month-over-month price changes (%)
    - Identify trend direction (up/down/sideways)
    - Compute key metrics: avg closing price, volatility, volume trends

    ### Visualization
    Generate using `code_interpreter`:
    - **Price chart**: Monthly OHLC data
    - **Volume chart**: Trading volume per month

    Ensure charts have clear titles, labels, and legends."""


def create_api_response(client: OpenAI, user_prompt: str, server_url: str, api_key: str):
    """
    Create a response using OpenAI's Responses API with MCP server integration.

    Args:
        client: OpenAI client instance
        user_prompt: User's analysis request
        server_url: MCP server URL
        api_key: Alpha Vantage API key

    Returns:
        Response object from OpenAI API
    """
    return client.responses.create(
        model=MODEL,
        tools=[
            {
                "type": "mcp",
                "server_label": MCP_SERVER_LABEL,
                "server_description": "Alpha Vantage MCP Server for financial market data",
                "server_url": server_url,
                "authorization": api_key,
                "require_approval": "never",
            },
            {
                "type": "code_interpreter",
                "container": {"type": "auto", "memory_limit": "4g"}
            }
        ],
        input=user_prompt,
    )


def save_visualizations(client: OpenAI, response) -> None:
    """
    Extract and save visualization files from the API response.

    Args:
        client: OpenAI client instance
        response: API response object containing potential visualizations
    """
    print("\n" + "="*80)
    print("💾 SAVING VISUALIZATIONS")
    print("="*80)

    for message in response.messages:
        for content in message.content:
            if hasattr(content, 'annotations'):
                for annotation in content.annotations:
                    if annotation.type == 'container_file_citation':
                        container_id = annotation.container_id
                        file_id = annotation.file_id

                        print(f"→ Found visualization: container_id={container_id}, file_id={file_id}")

                        # Download file content
                        file_content = client.containers.files.content.retrieve(
                            container_id=container_id,
                            file_id=file_id
                        )

                        # Save locally
                        with open(OUTPUT_IMAGE_PATH, 'wb') as f:
                            f.write(file_content.read())

                        print(f"✓ Saved visualization to: {OUTPUT_IMAGE_PATH}")

    print("="*80 + "\n")


def handle_authentication_error(error: AuthenticationError) -> None:
    """Handle authentication errors with helpful messages."""
    print("\n❌ AUTHENTICATION ERROR:")
    print(f"   The API key is invalid or expired!")
    print(f"   Details: {str(error)}")
    print("\n   Solutions:")
    print("   1. Check if the API key is correct")
    print("   2. Generate a new API key at: https://platform.openai.com/api-keys")
    print("   3. Verify that your OpenAI account is still active")


def handle_api_error(error: APIError) -> None:
    """Handle API errors with helpful messages."""
    print("\n❌ API ERROR:")
    print(f"   Status Code: {error.status_code if hasattr(error, 'status_code') else 'Unknown'}")
    print(f"   Details: {str(error)}")
    print("\n   Possible causes:")
    print("   - Quota exceeded (no credits remaining)")
    print("   - Temporary issues at OpenAI")
    print("   - Invalid request format")


def handle_openai_error(error: OpenAIError) -> None:
    """Handle general OpenAI errors with helpful messages."""
    print("\n❌ OPENAI ERROR:")
    print(f"   Details: {str(error)}")
    print("\n   Please check:")
    print("   - API key validity")
    print("   - Network connection")
    print("   - OpenAI service status: https://status.openai.com/")


def handle_unexpected_error(error: Exception) -> None:
    """Handle unexpected errors with helpful messages."""
    print("\n❌ UNEXPECTED ERROR:")
    print(f"   Type: {type(error).__name__}")
    print(f"   Details: {str(error)}")
    print("\n   Please contact support with this error message.")


def call_openai() -> None:
    """
    Main function to call OpenAI Responses API with Alpha Vantage MCP Server.

    This function orchestrates the entire workflow:
    1. Validates environment variables
    2. Initializes OpenAI client
    3. Creates API request with MCP integration
    4. Processes and displays results
    5. Saves any generated visualizations
    """
    # Validate environment variables
    openai_api_key, alphavantage_api_key, server_url = validate_environment_variables()
    if not all([openai_api_key, alphavantage_api_key, server_url]):
        return

    try:
        # Initialize OpenAI client
        print("→ Initializing OpenAI client...")
        client = OpenAI(api_key=openai_api_key)

        # Get analysis prompt
        user_prompt = get_analysis_prompt()

        # Display request information
        print("\n" + "="*80)
        print("🤖 OPENAI RESPONSES API CALL")
        print("="*80)
        print(f"Model: {MODEL}")
        print(f"MCP Server: {MCP_SERVER_LABEL}")
        print(f"MCP URL: {server_url}")
        print(f"User Prompt:\n{user_prompt}")
        print("-"*80)

        # Call OpenAI Responses API with MCP server
        response = create_api_response(client, user_prompt, server_url, alphavantage_api_key)

        # Display complete response
        print("\n" + "="*80)
        print("📥 OPENAI RESPONSES API - COMPLETE RESPONSE")
        print("="*80)
        print(json.dumps(response.model_dump(), indent=2))
        print("="*80 + "\n")

        # Display final output
        print("\n" + "="*80)
        print("📊 FINAL OUTPUT")
        print("="*80)
        print(response.output)
        print("="*80 + "\n")
        print(response.output_text)

        # Extract and save visualizations
        save_visualizations(client, response)

    except AuthenticationError as e:
        handle_authentication_error(e)
    except APIError as e:
        handle_api_error(e)
    except OpenAIError as e:
        handle_openai_error(e)
    except Exception as e:
        handle_unexpected_error(e)


if __name__ == '__main__':
    call_openai()
    