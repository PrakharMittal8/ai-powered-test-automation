from datetime import datetime


class ReportService:

    def generate_bug_report(
        self,
        failure_data,
        analysis: dict,
        similar_count: int,
        environment_pattern: dict = None,
        same_page_failures: dict = None,
        tool_reasoning: str = ""
    ) -> str:

        recommended_fixes = "\n".join(
            f"- {fix}" for fix in analysis.get("recommendedFix", [])
        ) or "- No fixes suggested"

        investigation_section = ""

        if tool_reasoning:
            investigation_section += f"""
## Agent Investigation

**Reasoning:** {tool_reasoning}
"""

        if environment_pattern and environment_pattern.get("pattern") != "NO_HISTORY":
            investigation_section += f"""
### Environment Pattern

- **Pattern:** {environment_pattern.get("pattern")}
- **Total Matching Failures:** {environment_pattern.get("totalMatching")}
- **Insight:** {environment_pattern.get("insight")}
"""

        if same_page_failures and same_page_failures.get("relatedCount", 0) > 0:
            related = ", ".join(same_page_failures.get("relatedTests", []))
            investigation_section += f"""
### Same Page Failures

- **Related Failures Found:** {same_page_failures.get("relatedCount")}
- **Related Tests:** {related}
- **Insight:** {same_page_failures.get("insight")}
"""

        report = f"""# Bug Report — {failure_data.testName}

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
**Environment:** {failure_data.environment}
**Timestamp:** {failure_data.timestamp}

---

## Failure Summary

| Field | Value |
|---|---|
| Failure Type | {analysis.get("failureType", "UNKNOWN")} |
| Confidence | {analysis.get("confidence", "UNKNOWN")} |
| Is Transient | {analysis.get("isTransient", False)} |
| Should Retry | {analysis.get("shouldRetry", False)} |
| Similar Past Failures | {similar_count} |

---

## Root Cause

{analysis.get("rootCause", "Not determined")}

---

## Recommended Fix

{recommended_fixes}

---

## Framework Suggestion

{analysis.get("frameworkSuggestion", "None")}

{investigation_section}

---

## Exception

{failure_data.exceptionMessage}

## Stack Trace

{failure_data.stackTrace}
"""
        return report.strip()