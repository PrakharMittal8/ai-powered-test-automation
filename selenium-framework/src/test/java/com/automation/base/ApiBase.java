package com.automation.base;

import com.automation.utils.ConfigReader;

import io.restassured.RestAssured;

import org.testng.annotations.BeforeClass;

public class ApiBase {

    @BeforeClass
    public void setupAPI() {

        RestAssured.baseURI =
                ConfigReader.get("apiBaseUrl");
    }
}
