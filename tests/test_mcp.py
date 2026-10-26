import pytest
from mcp import Client

from mcp_server.server import mcp


@pytest.mark.anyio
async def test_mcp_tools_are_registered():

    async with Client(mcp) as client:

        result = await client.list_tools()

        tool_names = {
            tool.name
            for tool in result.tools
        }

        expected_tools = {
            "search_products",
            "get_product_details",
            "check_inventory",
            "get_quote",
            "get_support_ticket",
            "prepare_quote_draft",
            "create_quote_draft",
            "prepare_support_ticket",
            "create_support_ticket",
        }

        assert expected_tools.issubset(
            tool_names
        )