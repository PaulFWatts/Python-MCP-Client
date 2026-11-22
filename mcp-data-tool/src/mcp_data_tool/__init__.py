import csv
import pathlib

from mcp.server.fastmcp import FastMCP


DATA_FOLDER = (pathlib.Path(__file__).parent.parent.parent / "data").resolve()
mcp_server = FastMCP("Sales MCP server")


@mcp_server.prompt("Sales analysis")
def get_sales_analysis_prompt() -> str:
    return """Determine the total number of sales
    done across all customers and also tell me the
    total amount spent by Bob."""


@mcp_server.resource("file://data/sales.csv")
def get_sales() -> str:
    """Retrieve the CSV with all sales."""
    with open(DATA_FOLDER / "sales.csv", "r") as f:
        return f.read()


@mcp_server.tool()
def get_sales_from_customer(customer_name: str) -> list[int]:
    """Get a list of all sales totals for a given customer."""
    sales: list[int] = []
    with open(DATA_FOLDER / "sales.csv", "r") as f:
        reader = csv.reader(f)
        for name, paid in reader:
            if name == customer_name:
                sales.append(int(paid))
    return sales


def main() -> None:
    mcp_server.run()
