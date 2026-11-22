import asyncio
from contextlib import AsyncExitStack
from typing import Self

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """MCP client that connects to arbitrary MCP servers.

    You tell the client what server to connect to by specifying
    the shell command that _starts_ the server.

    Usage:
        async with MCPClient(server_command) as client:
            ...
    """

    def __init__(self, server_command: str) -> None:
        self.server_command = server_command
        self.exit_stack = AsyncExitStack()

    async def __aenter__(self) -> Self:
        self.client_session = await self._connect_to_server()
        return self

    async def __aexit__(self, *_) -> None:
        await self.exit_stack.aclose()

    async def _connect_to_server(self) -> ClientSession:
        read, write = await self.exit_stack.enter_async_context(
            stdio_client(
                server=StdioServerParameters(
                    command="sh",
                    args=[
                        "-c",
                        f"{self.server_command} 2>/dev/null",
                    ]
                )
            )
        )
        client_session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await client_session.initialize()
        return client_session


async def main():
    async with MCPClient("mcp-data"):
        print("Connected to the MCP server!")


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()