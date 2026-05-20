from app.services.dashboard_service import DashboardService

dashboard_service = DashboardService()


def re_analyze_tool(failure_data, original_analysis, openai_service) -> dict:
    """
    Called when confidence is LOW.
    Re-calls LLM with a sharper prompt focused on stack trace.
    Returns a new analysis dict replacing the original.
    """
    import json
    from app.prompts.reanalysis_prompt import build_reanalysis_prompt

    print("\n[TOOL] re_analyze_tool called — confidence was LOW\n")

    prompt = build_reanalysis_prompt(failure_data, original_analysis)
    llm_response = openai_service.analyze_failure(prompt)

    try:
        new_analysis = json.loads(llm_response)
        print(
            f"[TOOL] Re-analysis complete. "
            f"New confidence: {new_analysis.get('confidence')}\n"
        )
        return new_analysis
    except Exception:
        print("[TOOL] Re-analysis parse failed. Keeping original.\n")
        return original_analysis


def check_environment_pattern_tool(failure_type: str) -> dict:
    """
    Called when repeat count >= 3.
    Checks if repeated failures are in same environment or spread across envs.
    Returns pattern summary.
    """
    print("\n[TOOL] check_environment_pattern_tool called\n")

    all_entries = dashboard_service.get_all()

    matching = [
        e for e in all_entries
        if e.get("failureType", "").upper() == failure_type.upper()
    ]

    if not matching:
        return {
            "totalMatching": 0,
            "environments": [],
            "pattern": "NO_HISTORY",
            "insight": "No previous failures of this type found."
        }

    env_counts = {}
    for entry in matching:
        env = entry.get("environment", "UNKNOWN")
        env_counts[env] = env_counts.get(env, 0) + 1

    if len(env_counts) == 1:
        env_name = list(env_counts.keys())[0]
        pattern = "SINGLE_ENVIRONMENT"
        insight = (
            f"All {len(matching)} occurrences are in '{env_name}' only. "
            f"Likely an environment-specific issue."
        )
    else:
        pattern = "MULTIPLE_ENVIRONMENTS"
        env_summary = ", ".join(
            f"{env}({count})" for env, count in env_counts.items()
        )
        insight = (
            f"{len(matching)} occurrences spread across environments: "
            f"{env_summary}. Likely a code-level or framework issue."
        )

    print(f"[TOOL] Environment pattern: {pattern} — {insight}\n")

    return {
        "totalMatching": len(matching),
        "environments": env_counts,
        "pattern": pattern,
        "insight": insight
    }


def check_same_page_failures_tool(test_name: str) -> dict:
    """
    Called when failure type is ELEMENT_NOT_FOUND or TIMEOUT.
    Checks if other tests with similar names are also failing.
    Returns related failure summary.
    """
    print("\n[TOOL] check_same_page_failures_tool called\n")

    all_entries = dashboard_service.get_all()

    # Extract page hint from test name
    # e.g. "testLoginPageSubmit" -> "login"
    name_lower = test_name.lower()
    words = [
        w for w in ["login", "home", "dashboard", "checkout",
                    "search", "profile", "register", "cart",
                    "payment", "settings", "admin", "landing"]
        if w in name_lower
    ]
    page_hint = words[0] if words else None

    if not page_hint:
        # Fall back to first meaningful word in test name
        parts = [
            p for p in name_lower.replace("test", "").split("_")
            if len(p) > 3
        ]
        page_hint = parts[0] if parts else None

    if not page_hint:
        return {
            "relatedCount": 0,
            "relatedTests": [],
            "insight": "Could not determine page context from test name."
        }

    related = [
        e for e in all_entries
        if page_hint in e.get("testName", "").lower()
        and e.get("testName") != test_name
    ]

    related_names = list({e["testName"] for e in related})

    if related:
        insight = (
            f"Found {len(related)} other failures on tests "
            f"containing '{page_hint}': {', '.join(related_names)}. "
            f"Possible page-level or shared component issue."
        )
    else:
        insight = (
            f"No other failures found for page context '{page_hint}'. "
            f"Issue appears isolated to this test."
        )

    print(f"[TOOL] Same-page pattern: {insight}\n")

    return {
        "relatedCount": len(related),
        "relatedTests": related_names,
        "pageHint": page_hint,
        "insight": insight
    }