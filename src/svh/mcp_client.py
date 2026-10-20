"""Thin MCP v2 tool adapter; deepagents retains ownership of the agent loop."""

from contextlib import asynccontextmanager

from langchain_core.tools import StructuredTool, ToolException
from mcp import Client
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client


@asynccontextmanager
async def connect(url, token):
    async with create_mcp_http_client(headers={"Authorization": "Bearer " + token}) as http:
        transport = streamable_http_client(url, http_client=http, max_sse_event_size=24 * 1024 ** 2)
        async with Client(transport, read_timeout_seconds=100) as client:
            yield client


async def harness_tools(client):
    """Preserve structured evidence and images, rather than flattening screenshots."""
    remote = await client.list_tools()

    def adapt(spec):
        async def invoke(**arguments):
            result = await client.call_tool(spec.name, arguments)
            content = []
            for block in result.content:
                if block.type == "text":
                    content.append({"type": "text", "text": block.text})
                elif block.type == "image":
                    content.append({"type": "image_url", "image_url": {
                        "url": f"data:{block.mime_type};base64,{block.data}"}})
                else:
                    raise ToolException("Unsupported MCP evidence content type")
            if result.is_error:
                raise ToolException("; ".join(item["text"] for item in content if item["type"] == "text"))
            return content, result.structured_content

        return StructuredTool.from_function(
            coroutine=invoke, name=spec.name, description=spec.description or spec.name,
            args_schema=spec.input_schema, response_format="content_and_artifact", handle_tool_error=True,
        )

    return [adapt(spec) for spec in remote.tools]
