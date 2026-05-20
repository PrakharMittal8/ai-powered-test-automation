package com.automation.ai;

import io.restassured.response.Response;
import org.json.JSONObject;

import static io.restassured.RestAssured.given;

public class AIAnalysisService {

    private static final String AI_BASE_URL =
            "http://127.0.0.1:8000/analyze";

    public static String analyzeFailure(
            String testName,
            String exceptionMessage,
            String stackTrace,
            String screenshotPath,
            String pageSourcePath,
            String browserLogs,
            String timestamp,
            String environment
    ) {

        JSONObject requestBody = new JSONObject();

        requestBody.put("testName", testName);
        requestBody.put("exceptionMessage", exceptionMessage);
        requestBody.put("stackTrace", stackTrace);
        requestBody.put("screenshotPath", screenshotPath);
        requestBody.put("pageSourcePath", pageSourcePath);
        requestBody.put("browserLogs", browserLogs);
        requestBody.put("timestamp", timestamp);
        requestBody.put("environment", environment);

        Response response =
                given()
                        .header("Content-Type", "application/json")
                        .body(requestBody.toString())
                        .when()
                        .post(AI_BASE_URL);

        return response.asPrettyString();
    }
}
