# math_tools.py

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from perceive import Perceive

# Instantiate MCP server and Perceive class
mcp = FastMCP("Calculator")
perceive = Perceive()

@mcp.tool()
def show_reasoning(expression: str) -> TextContent:
    """Show step-by-step reasoning for a calculation."""
    reasoning = perceive.show_reasoning(expression)
    return TextContent(type="text", text=reasoning)

@mcp.tool()
def calculate(expression: str) -> TextContent:
    """Calculate the result of an expression."""
    result = perceive.parse_expression(expression)
    if result is None:
        return TextContent(type="text", text="Invalid expression or error in calculation.")
    return TextContent(type="text", text=str(result))

@mcp.tool()
def verify(expression: str, expected: float) -> TextContent:
    """Check if a calculation is correct."""
    is_correct = perceive.verify_calculation(expression, expected)
    return TextContent(type="text", text="Correct" if is_correct else "Incorrect")

@mcp.tool()
def check_consistency(expression: str, result: float) -> TextContent:
    """Check if a calculation is consistent with mathematical rules."""
    is_consistent = perceive.check_consistency(expression, result)
    return TextContent(type="text", text="Consistent" if is_consistent else "Inconsistent")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()
    else:
        mcp.run(transport="stdio")