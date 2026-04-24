import json
import os
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """MCP Client that connects to the local ShopBot MCP Server via stdio."""

    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._tools: list[dict] = []

    async def connect(self):
        """Start the MCP server subprocess and discover tools."""
        backend_root = str(Path(__file__).parents[1])
        env = os.environ.copy()
        existing_pp = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{backend_root}{os.pathsep}{existing_pp}".strip(os.pathsep)

        server_params = StdioServerParameters(
            command="python",
            args=["-m", "app.mcp_server"],
            env=env,
        )
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()
        tools_result = await self.session.list_tools()
        self._tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in tools_result.tools
        ]

    def get_tools(self) -> list[dict]:
        """Return tool schemas in Anthropic-compatible format."""
        return self._tools

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Execute a tool on the MCP server and return its JSON/text result."""
        if self.session is None:
            raise RuntimeError("MCP client not connected")
        result = await self.session.call_tool(name, arguments)
        texts = [item.text for item in result.content if hasattr(item, "text")]
        if texts:
            return texts[0]
        return json.dumps([item.model_dump() for item in result.content])

    async def close(self):
        """Shut down the subprocess and clean up resources."""
        await self.exit_stack.aclose()
