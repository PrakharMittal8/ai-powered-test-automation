import asyncio
import json
import httpx
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

app = Server("ai-failure-analysis")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="analyze_failure",
            description=(
                "Analyze a Selenium test failure using AI. "
                "Provide the test name, exception message, stack trace, "
                "browser logs, and environment. Returns root cause, "
                "failure type, confidence, recommended fix, and agent "
                "investigation results."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "testName": {
                        "type": "string",
                        "description": "Name of the failed Selenium test"
                    },
                    "exceptionMessage": {
                        "type": "string",
                        "description": "The exception or error message"
                    },
                    "stackTrace": {
                        "type": "string",
                        "description": "Full stack trace of the failure"
                    },
                    "screenshotPath": {
                        "type": "string",
                        "description": "Path to screenshot, can be empty string"
                    },
                    "pageSourcePath": {
                        "type": "string",
                        "description": "Path to page source, can be empty string"
                    },
                    "browserLogs": {
                        "type": "string",
                        "description": "Browser console logs, can be empty string"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Timestamp of failure in ISO format"
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment where test ran e.g. QA, STAGING, PROD"
                    }
                },
                "required": [
                    "testName",
                    "exceptionMessage",
                    "stackTrace",
                    "screenshotPath",
                    "pageSourcePath",
                    "browserLogs",
                    "timestamp",
                    "environment"
                ]
            }
        ),

        types.Tool(
            name="get_dashboard_summary",
            description=(
                "Get a LIVE real-time summary of all test failures. "
                "Always fetches fresh data from the system. "
                "Returns total failures, breakdown by failure type, "
                "confidence distribution, transient vs permanent count, "
                "and repeat failure patterns. "
                "Pass current_time to ensure fresh results every call."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "current_time": {
                        "type": "string",
                        "description": (
                            "Current timestamp to ensure fresh data fetch. "
                            "Pass current date and time as a string."
                        )
                    }
                },
                "required": ["current_time"]
            }
        ),

        types.Tool(
            name="get_recent_failures",
            description=(
                "Get the LATEST real-time test failures from the live dashboard. "
                "Always fetches fresh data — never uses cached results. "
                "Pass current_time to guarantee a live fetch every single call. "
                "Returns failure details including test name, failure type, "
                "root cause, confidence, and agent reasoning."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent failures to return. Default is 5.",
                        "default": 5
                    },
                    "current_time": {
                        "type": "string",
                        "description": (
                            "Current timestamp to ensure fresh data fetch. "
                            "Pass current date and time as a string. "
                            "Example: '2024-01-15 10:30:00'"
                        )
                    }
                },
                "required": ["current_time"]
            }
        )
    ]


@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:

    async with httpx.AsyncClient(timeout=60.0) as client:

        if name == "analyze_failure":
            try:
                payload = {
                    "testName": arguments.get("testName", ""),
                    "exceptionMessage": arguments.get("exceptionMessage", ""),
                    "stackTrace": arguments.get("stackTrace", ""),
                    "screenshotPath": arguments.get("screenshotPath", ""),
                    "pageSourcePath": arguments.get("pageSourcePath", ""),
                    "browserLogs": arguments.get("browserLogs", ""),
                    "timestamp": arguments.get("timestamp", ""),
                    "environment": arguments.get("environment", "")
                }

                response = await client.post(
                    f"{FASTAPI_BASE_URL}/analyze",
                    json=payload
                )
                data = response.json()

                analysis = data.get("analysis", {})
                agent = data.get("agentResult", {})

                result = {
                    "fetchedAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "failureType": analysis.get("failureType", "UNKNOWN"),
                    "confidence": analysis.get("confidence", "UNKNOWN"),
                    "rootCause": analysis.get("rootCause", ""),
                    "isTransient": analysis.get("isTransient", False),
                    "shouldRetry": analysis.get("shouldRetry", False),
                    "recommendedFix": analysis.get("recommendedFix", []),
                    "frameworkSuggestion": analysis.get("frameworkSuggestion", ""),
                    "similarFailuresFound": data.get("similarFailuresFound", 0),
                    "agentToolsUsed": agent.get("toolsUsed", []),
                    "agentReasoning": agent.get("toolReasoning", ""),
                    "environmentPattern": agent.get("environmentPattern"),
                    "samePageFailures": agent.get("samePageFailures")
                }

                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error calling analyze endpoint: {str(e)}"
                )]

        elif name == "get_dashboard_summary":
            try:
                response = await client.get(
                    f"{FASTAPI_BASE_URL}/dashboard-data"
                )
                entries = response.json()

                if not entries:
                    return [types.TextContent(
                        type="text",
                        text="No failures recorded yet."
                    )]

                type_counts = {}
                for e in entries:
                    ft = e.get("failureType", "UNKNOWN")
                    type_counts[ft] = type_counts.get(ft, 0) + 1

                conf_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
                for e in entries:
                    c = e.get("confidence", "UNKNOWN").upper()
                    if c in conf_counts:
                        conf_counts[c] += 1
                    else:
                        conf_counts["UNKNOWN"] += 1

                transient = sum(
                    1 for e in entries if e.get("isTransient") is True
                )
                permanent = sum(
                    1 for e in entries if e.get("isTransient") is False
                )

                repeats = {
                    ft: count
                    for ft, count in type_counts.items()
                    if count > 1
                }

                summary = {
                    "fetchedAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "totalFailures": len(entries),
                    "failureTypeBreakdown": type_counts,
                    "confidenceBreakdown": conf_counts,
                    "transientFailures": transient,
                    "permanentFailures": permanent,
                    "repeatPatterns": repeats
                }

                return [types.TextContent(
                    type="text",
                    text=json.dumps(summary, indent=2)
                )]

            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error fetching dashboard data: {str(e)}"
                )]

        elif name == "get_recent_failures":
            try:
                limit = arguments.get("limit", 5)

                response = await client.get(
                    f"{FASTAPI_BASE_URL}/dashboard-data"
                )
                entries = response.json()

                if not entries:
                    return [types.TextContent(
                        type="text",
                        text="No failures recorded yet."
                    )]

                recent = list(reversed(entries))[:limit]

                simplified = []
                for e in recent:
                    simplified.append({
                        "id": e.get("id"),
                        "timestamp": e.get("timestamp"),
                        "testName": e.get("testName"),
                        "environment": e.get("environment"),
                        "failureType": e.get("failureType"),
                        "confidence": e.get("confidence"),
                        "isTransient": e.get("isTransient"),
                        "rootCause": e.get("rootCause"),
                        "agentReasoning": e.get("agentReasoning", ""),
                        "similarFailuresFound": e.get("similarFailuresFound", 0)
                    })

                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "fetchedAt": datetime.utcnow().strftime(
                            "%Y-%m-%d %H:%M:%S UTC"
                        ),
                        "totalInSystem": len(entries),
                        "showing": len(simplified),
                        "failures": simplified
                    }, indent=2)
                )]

            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error fetching recent failures: {str(e)}"
                )]

        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())