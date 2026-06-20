"""
mcp_client.py — Low-level MCP communication layer for Agent Arena.
Opens a fresh HTTP connection per call to avoid session timeouts.
"""

import httpx
import json
import os
import uuid

MCP_ENDPOINT = "https://agent-arena-623774504237.asia-southeast1.run.app/mcp"


async def mcp_call(tool: str, args: dict) -> str:
    """
    Call an Arena MCP tool via JSON-RPC over HTTP.
    Returns the text content of the response.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": args
        },
        "id": str(uuid.uuid4())
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            MCP_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()

    # Extract text from result content blocks
    result = data.get("result", {})
    content = result.get("content", [])
    text_parts = [block.get("text", "") for block in content if block.get("type") == "text"]
    return "\n".join(filter(None, text_parts))


async def register_agent(id_token: str, name: str, stack: str,
                          github_url: str, linkedin_url: str,
                          team_members: str = "") -> str:
    """Register MetaMind with the Arena. Safe to call multiple times."""
    return await mcp_call("register_agent", {
        "idToken": id_token,
        "name": name,
        "stack": stack,
        "githubUrl": github_url,
        "linkedinUrl": linkedin_url,
        "teamMembers": team_members
    })


async def get_tasks(id_token: str, agent_id: str) -> dict:
    """Fetch current task. Returns parsed dict or raw string on failure."""
    raw = await mcp_call("get_tasks", {
        "idToken": id_token,
        "agentId": agent_id
    })
    try:
        task = json.loads(raw)
        # Ensure we actually got a task dict, not a string or list
        if isinstance(task, dict):
            return task
        return {"raw": str(raw)}
    except Exception:
        return {"raw": raw}


async def submit_task(id_token: str, agent_id: str,
                       task_id: str, content: str,
                       metadata: dict = None) -> str:
    """Submit answer for AI evaluation. Returns score and feedback."""
    return await mcp_call("submit_task", {
        "idToken": id_token,
        "agentId": agent_id,
        "taskId": task_id,
        "executionId": str(uuid.uuid4()),
        "content": content,
        "metadata": metadata or {}
    })


async def skip_task(id_token: str, agent_id: str,
                     task_id: str, reason: str = "") -> str:
    """Skip the current task and unlock a fresh one."""
    return await mcp_call("skip_task", {
        "idToken": id_token,
        "agentId": agent_id,
        "taskId": task_id,
        "reason": reason
    })
