import asyncio
import json

import click
from pydantic import AnyUrl
import rich

from . import MCPClient


@click.group()
def mcp_cli():
    """CLI for the MCP client."""


@mcp_cli.command(help="Call a tool.")
@click.argument("server_command")
@click.argument("tool")
@click.argument("arguments")
def call(server_command: str, tool: str, arguments: str) -> None:
    asyncio.run(_call(server_command, tool, arguments))


async def _call(server_command: str, tool: str, arguments: str) -> None:
    args_dict = json.loads(arguments)
    async with MCPClient(server_command) as client:
        result = await client.client_session.call_tool(tool, args_dict)
        print(result)


@mcp_cli.command(help="Fetch a resource by name.")
@click.argument("server_command")
@click.argument("uri")
def fetch(server_command: str, uri: str) -> None:
    asyncio.run(_fetch(server_command, uri))


async def _fetch(server_command: str, uri: str) -> None:
    async with MCPClient(server_command) as client:
        resource = await client.client_session.read_resource(AnyUrl(uri))
        for part in resource.contents:
            print(part)


@mcp_cli.command(help="Get a prompt from its name.")
@click.argument("server_command")
@click.argument("prompt_name")
def get(server_command: str, prompt_name: str) -> None:
    asyncio.run(_get(server_command, prompt_name))


async def _get(server_command: str, prompt_name: str) -> None:
    async with MCPClient(server_command) as client:
        prompt = await client.client_session.get_prompt(prompt_name)
        for message in prompt.messages:
            print(message)


@mcp_cli.command(
    help="List all tools, resources, and prompts,"
    + "from the given MCP server."
)
@click.argument("server_command")
def ls(server_command: str) -> None:
    asyncio.run(_ls(server_command))


async def _ls(server_command: str) -> None:
    async with MCPClient(server_command) as client:
        print("=== Tools ===")
        tools = (await client.client_session.list_tools()).tools
        for item in tools:
            description = item.description or "<No description>"
            print(f" - {item.name} - {description}")
            rich.print(item.inputSchema)
        print()

        print("=== Resources ===")
        resources = (await client.client_session.list_resources()).resources
        for item in resources:
            description = item.description or "<No description>"
            print(f" - {item.name} - {item.uri} - {description}")
        print()

        print("=== Prompts ===")
        prompts = (await client.client_session.list_prompts()).prompts
        for item in prompts:
            description = item.description or "<No description>"
            print(f" - {item.name} - {description}")


@mcp_cli.command(help="Test the connection to the given MCP server.")
@click.argument("server_command")
def connect(server_command: str) -> None:
    asyncio.run(_connect(server_command))


async def _connect(server_command: str) -> None:
    async with MCPClient(server_command):
        print("Connected to the server!")