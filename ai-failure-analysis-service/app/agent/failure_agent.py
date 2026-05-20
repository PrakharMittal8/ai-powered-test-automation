from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from app.models.failure_models import FailureRequest
from app.services.report_service import ReportService
from app.services.dashboard_service import DashboardService
from app.services.openai_service import OpenAIService
from app.agent.tools import (
    re_analyze_tool,
    check_environment_pattern_tool,
    check_same_page_failures_tool
)

# ── State ──────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    failure_data: FailureRequest
    analysis: dict
    similar_count: int
    failure_type: str
    repeat_count: int
    tools_to_call: list
    tool_reasoning: str
    environment_pattern: Optional[dict]
    same_page_failures: Optional[dict]
    bug_report: str
    dashboard_entry: Optional[dict]

# ── Services ───────────────────────────────────────────────────────────────────

report_service = ReportService()
dashboard_service = DashboardService()
openai_service = OpenAIService()

# ── Node 1: Classify ───────────────────────────────────────────────────────────

def classify_failure(state: AgentState) -> AgentState:
    print("\n[AGENT] Node: classify_failure\n")
    failure_type = state["analysis"].get("failureType", "UNKNOWN").upper()
    state["failure_type"] = failure_type
    print(f"[AGENT] Classified as: {failure_type}\n")
    return state

# ── Node 2: Check Trends ───────────────────────────────────────────────────────

def check_trends(state: AgentState) -> AgentState:
    print("\n[AGENT] Node: check_trends\n")
    repeat_count = dashboard_service.get_repeat_count(state["failure_type"])
    state["repeat_count"] = repeat_count
    print(f"[AGENT] Repeat count for '{state['failure_type']}': {repeat_count}\n")
    return state

# ── Node 3: Agent Decides Tools ────────────────────────────────────────────────

def agent_decide(state: AgentState) -> AgentState:
    print("\n[AGENT] Node: agent_decide — LLM choosing tools\n")

    decision = openai_service.decide_tools(
        state["failure_data"],
        state["analysis"],
        state["repeat_count"]
    )

    state["tools_to_call"] = decision.get("tools_to_call", [])
    state["tool_reasoning"] = decision.get("reasoning", "")

    print(f"[AGENT] Tools chosen: {state['tools_to_call']}\n")
    print(f"[AGENT] Reasoning: {state['tool_reasoning']}\n")

    return state

# ── Node 4: Execute Tools ──────────────────────────────────────────────────────

def execute_tools(state: AgentState) -> AgentState:
    print("\n[AGENT] Node: execute_tools\n")

    tools = state["tools_to_call"]

    if "re_analyze" in tools:
        new_analysis = re_analyze_tool(
            state["failure_data"],
            state["analysis"],
            openai_service
        )
        state["analysis"] = new_analysis
        state["failure_type"] = new_analysis.get(
            "failureType", state["failure_type"]
        ).upper()

    if "check_environment_pattern" in tools:
        state["environment_pattern"] = check_environment_pattern_tool(
            state["failure_type"]
        )
    else:
        state["environment_pattern"] = None

    if "check_same_page_failures" in tools:
        state["same_page_failures"] = check_same_page_failures_tool(
            state["failure_data"].testName
        )
    else:
        state["same_page_failures"] = None

    return state

# ── Node 5: Generate Bug Report ────────────────────────────────────────────────

def generate_bug_report(state: AgentState) -> AgentState:
    print("\n[AGENT] Node: generate_bug_report\n")
    report = report_service.generate_bug_report(
        state["failure_data"],
        state["analysis"],
        state["similar_count"],
        state["environment_pattern"],
        state["same_page_failures"],
        state["tool_reasoning"]
    )
    state["bug_report"] = report
    print("[AGENT] Bug report generated.\n")
    return state

# ── Node 6: Log to Dashboard ───────────────────────────────────────────────────

def log_to_dashboard(state: AgentState) -> AgentState:
    print("\n[AGENT] Node: log_to_dashboard\n")
    entry = dashboard_service.log_failure(
        state["failure_data"],
        state["analysis"],
        state["similar_count"],
        state["bug_report"],
        state["tool_reasoning"],
        state["environment_pattern"],
        state["same_page_failures"]
    )
    state["dashboard_entry"] = entry
    return state

# ── Build Graph ────────────────────────────────────────────────────────────────

def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("classify_failure", classify_failure)
    graph.add_node("check_trends", check_trends)
    graph.add_node("agent_decide", agent_decide)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("generate_bug_report", generate_bug_report)
    graph.add_node("log_to_dashboard", log_to_dashboard)

    graph.set_entry_point("classify_failure")

    graph.add_edge("classify_failure", "check_trends")
    graph.add_edge("check_trends", "agent_decide")
    graph.add_edge("agent_decide", "execute_tools")
    graph.add_edge("execute_tools", "generate_bug_report")
    graph.add_edge("generate_bug_report", "log_to_dashboard")
    graph.add_edge("log_to_dashboard", END)

    return graph.compile()


agent = build_agent()


def run_agent(
    failure_data: FailureRequest,
    analysis: dict,
    similar_count: int
) -> dict:
    initial_state: AgentState = {
        "failure_data": failure_data,
        "analysis": analysis,
        "similar_count": similar_count,
        "failure_type": "",
        "repeat_count": 0,
        "tools_to_call": [],
        "tool_reasoning": "",
        "environment_pattern": None,
        "same_page_failures": None,
        "bug_report": "",
        "dashboard_entry": None
    }

    final_state = agent.invoke(initial_state)

    return {
        "failureType": final_state["failure_type"],
        "repeatCount": final_state["repeat_count"] + 1,
        "toolsUsed": final_state["tools_to_call"],
        "toolReasoning": final_state["tool_reasoning"],
        "environmentPattern": final_state["environment_pattern"],
        "samePageFailures": final_state["same_page_failures"],
        "bugReport": final_state["bug_report"],
        "dashboardEntry": final_state["dashboard_entry"]
    }