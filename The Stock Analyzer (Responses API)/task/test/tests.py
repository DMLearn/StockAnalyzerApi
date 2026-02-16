from hstest import dynamic_test, StageTest, CheckResult, TestedProgram
import re

class StockAnalyzerTest(StageTest):

    @dynamic_test(time_limit=0)
    def run_and_test_program(self):
        program = TestedProgram()
        output = program.start()

        if not output:
            return CheckResult.wrong("The program did not produce any output.")

        # Check for McpListTools
        mcp_list_match = re.search(r"McpListTools\((.*?)\)", output, re.DOTALL)
        if not mcp_list_match:
            return CheckResult.wrong("Looks like your MCP configuration is incorrect. "
                                     "The model should call McpListTools first.")
        mcp_list_content = mcp_list_match.group(1)

        if not re.search(r"server_label='AlphaVantage'", mcp_list_content, re.IGNORECASE):
            return CheckResult.wrong("Your MCP server's label should be 'AlphaVantage'.")
        if "TOOL_LIST" not in mcp_list_content:
            return CheckResult.wrong("McpListTools should contain 'TOOL_LIST'.")

        # Check for McpCall
        mcp_call_match = re.search(r"McpCall\((.*?)\)", output, re.DOTALL)
        if not mcp_call_match:
            return CheckResult.wrong("The output does not contain 'McpCall'.")
        mcp_call_content = mcp_call_match.group(1)

        if "type='mcp_call'" not in mcp_call_content:
            return CheckResult.wrong("McpCall should have type 'mcp_call'.")
        if "name='TOOL_CALL'" not in mcp_call_content:
            return CheckResult.wrong("McpCall should have name 'TOOL_CALL'.")
        if not re.search(r"server_label='AlphaVantage'", mcp_call_content, re.IGNORECASE):
            return CheckResult.wrong("Your MCP server's label should be 'AlphaVantage'.")

        if 'TIME_SERIES_DAILY' not in mcp_call_content:
            return CheckResult.wrong("McpCall arguments should contain tool_name 'TIME_SERIES_DAILY'."
                                     "Ensure your prompt is direct and specific.")
        if 'symbol' not in mcp_call_content or 'AAPL' not in mcp_call_content:
            return CheckResult.wrong("McpCall arguments should contain symbol 'AAPL'."
                                     "Ensure your prompt is direct and specific.")

        if "ResponseOutputMessage" not in output:
            return CheckResult.wrong("The output does not contain 'ResponseOutputMessage'."
                                     "Did you print `response.output`?")
        if not re.search(r"id='msg_[a-zA-Z0-9]+'", output):
            return CheckResult.wrong("The output message ID is incorrect. This is likely due to a formatting issue in the model output.")
        if not re.search(r"role='assistant'", output):
            return CheckResult.wrong("The output should be from the assistant role. This is likely due to a formatting issue in the model output.")
        if not re.search(r"status='completed'", output):
            return CheckResult.wrong("The output message status should be 'completed'.")
        if not re.search(r"type='message'", output):
            return CheckResult.wrong("The output message type should be 'message'.")
        if not re.search(r"type='output_text'", output):
            return CheckResult.wrong("The output message should contain content with type 'output_text'.")

        return CheckResult.correct()


if __name__ == '__main__':
    StockAnalyzerTest().run_tests()
