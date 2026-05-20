def build_reanalysis_prompt(failure_data, original_analysis):
    prompt = f"""
You are a Senior Software Test Architect.

A previous analysis of this Selenium failure returned LOW confidence.
Re-analyze focusing specifically on the stack trace and exception message.
Be more decisive this time — commit to a failure type and root cause.

Original Analysis (LOW confidence):
Failure Type: {original_analysis.get("failureType", "UNKNOWN")}
Root Cause: {original_analysis.get("rootCause", "")}

Current Failure Details:
Test Name: {failure_data.testName}
Exception: {failure_data.exceptionMessage}
Stack Trace: {failure_data.stackTrace}
Browser Logs: {failure_data.browserLogs}
Environment: {failure_data.environment}

Your task:
1. Identify exact failure category by reading stack trace carefully
2. Explain root cause precisely
3. Decide if failure is transient
4. Decide if retry is recommended
5. Suggest framework-level improvement
6. Suggest immediate fix

IMPORTANT:
Return ONLY valid JSON.
Do not return explanation outside JSON.
Confidence must be MEDIUM or HIGH — not LOW.

JSON FORMAT:
{{
    "failureType": "",
    "rootCause": "",
    "confidence": "",
    "recommendedFix": [],
    "frameworkSuggestion": "",
    "isTransient": true,
    "shouldRetry": true
}}
"""
    return prompt