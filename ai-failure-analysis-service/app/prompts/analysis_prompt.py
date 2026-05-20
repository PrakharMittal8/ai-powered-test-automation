def build_failure_analysis_prompt(
        failure_data,
        similar_failures
):

    similar_failure_text = ""

    if similar_failures:

        for idx, failure in enumerate(
                similar_failures,
                start=1
        ):

            similar_failure_text += f"""

Previous Failure {idx}

Exception:
{failure.get("exceptionMessage")}

Environment:
{failure.get("environment")}

"""

    else:

        similar_failure_text = (
            "No similar historical failures found."
        )

    prompt = f"""

You are a Senior Software Test Architect.

Analyze the Selenium automation failure.

Current Failure Details:

Test Name:
{failure_data.testName}

Exception:
{failure_data.exceptionMessage}

Stack Trace:
{failure_data.stackTrace}

Browser Logs:
{failure_data.browserLogs}

Environment:
{failure_data.environment}

Historical Similar Failures:
{similar_failure_text}

Your task:

1. Identify exact failure category
2. Explain root cause
3. Decide if failure is transient
4. Decide if retry is recommended
5. Suggest framework-level improvement
6. Suggest immediate fix

IMPORTANT:
Return ONLY valid JSON.
Do not return explanation outside JSON.

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