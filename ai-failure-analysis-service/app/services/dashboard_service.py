import json
import os
from datetime import datetime


class DashboardService:

    def __init__(self):
        self.dashboard_file = "data/dashboard_log.json"
        os.makedirs("data", exist_ok=True)

    def log_failure(
        self,
        failure_data,
        analysis: dict,
        similar_count: int,
        bug_report: str,
        tool_reasoning: str = "",
        environment_pattern: dict = None,
        same_page_failures: dict = None
    ):
        entry = {
            "id": self._generate_id(),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "testName": failure_data.testName,
            "environment": failure_data.environment,
            "failureType": analysis.get("failureType", "UNKNOWN"),
            "rootCause": analysis.get("rootCause", ""),
            "confidence": analysis.get("confidence", "UNKNOWN"),
            "isTransient": analysis.get("isTransient", False),
            "shouldRetry": analysis.get("shouldRetry", False),
            "similarFailuresFound": similar_count,
            "recommendedFix": analysis.get("recommendedFix", []),
            "frameworkSuggestion": analysis.get("frameworkSuggestion", ""),
            "exceptionMessage": failure_data.exceptionMessage,
            "bugReport": bug_report,
            "agentReasoning": tool_reasoning,
            "environmentPattern": environment_pattern,
            "samePageFailures": same_page_failures
        }

        existing = self._load()
        existing.append(entry)
        self._save(existing)

        print(f"\n[DASHBOARD] Entry logged. Total entries: {len(existing)}\n")
        return entry

    def get_all(self):
        return self._load()

    def get_repeat_count(self, failure_type: str) -> int:
        all_entries = self._load()
        return sum(
            1 for e in all_entries
            if e.get("failureType", "").upper() == failure_type.upper()
        )

    def _load(self):
        if not os.path.exists(self.dashboard_file):
            return []
        try:
            with open(self.dashboard_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except Exception:
            return []

    def _save(self, data):
        with open(self.dashboard_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _generate_id(self):
        existing = self._load()
        return len(existing) + 1