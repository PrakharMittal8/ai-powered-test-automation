package com.automation.api;

import com.automation.utils.ApiUtils;
import io.restassured.response.Response;
import org.json.JSONObject;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class LoginAPI {
    private static final Logger log = LogManager.getLogger(LoginAPI.class);

    public static Response login(String email, String password) {

        JSONObject requestBody = new JSONObject();
        

        requestBody.put("userEmail", email);
        requestBody.put("userPassword", password);
        log.info("Login API Request Body: " + requestBody.toString());

    Response response =
        ApiUtils.getRequestSpec()
                .body(requestBody.toString())
                .when()
                .post("/api/ecom/auth/login");

    log.info("Login API Response: " + response.asString());

    return response;
    }
}