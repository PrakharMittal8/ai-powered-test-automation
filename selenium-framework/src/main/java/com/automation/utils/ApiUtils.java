package com.automation.utils;

import io.restassured.specification.RequestSpecification;

import static io.restassured.RestAssured.given;

public class ApiUtils {

    public static RequestSpecification getRequestSpec() {

        return given()
                .relaxedHTTPSValidation()
                .header("Content-Type", "application/json");
    }

    public static RequestSpecification getRequestSpec(String token) {

        return given()
                .relaxedHTTPSValidation()
                .header("Authorization", token)
                .header("Content-Type", "application/json");
    }
}
