package com.automation.tests;

import com.automation.api.CartAPI;
import com.automation.api.LoginAPI;
import com.automation.api.ProductAPI;
import com.automation.base.ApiBase;

import io.restassured.response.Response;

import org.json.JSONArray;
import org.json.JSONObject;

import org.testng.Assert;
import org.testng.annotations.Test;
import com.automation.utils.ConfigReader;

public class ApiE2ETest extends ApiBase {

    @Test
    public void completeApiFlowTest() {

        //-----------------------------------
        // Step 1 → Login
        //-----------------------------------

        Response loginResponse =
                LoginAPI.login(
                        ConfigReader.get("username"),
                ConfigReader.get("password")
                );

        Assert.assertEquals(
                loginResponse.statusCode(),
                200
        );

        String token =
                loginResponse.jsonPath()
                        .getString("token");

        String userId =
                loginResponse.jsonPath()
                        .getString("userId");

        System.out.println(">>-----------------Token: " + token);
        System.out.println(">>-----------------User ID: " + userId);

        //-----------------------------------
        // Step 2 → Fetch all products
        //-----------------------------------

        Response productResponse =
                ProductAPI.getAllProducts(token);

        Assert.assertEquals(
                productResponse.statusCode(),
                200
        );

        JSONArray products =
                new JSONObject(
                        productResponse.asString()
                ).getJSONArray("data");

       String targetProductName =
        ConfigReader.get("productNameForAPI");
        // String targetProductName = "ZARA COAT 3";
        String targetProductId = "";

        for (int i = 0; i < products.length(); i++) {

            JSONObject product =
                    products.getJSONObject(i);

            String currentProductName =
                    product.getString("productName");

            if (currentProductName.equalsIgnoreCase(targetProductName)) {

                targetProductId =
                        product.getString("_id");

                break;
            }
        }

        Assert.assertFalse(
                targetProductId.isEmpty(),
                "Product ID not found"
        );

        System.out.println(">>-----------------Product ID: " + targetProductId);

        //-----------------------------------
        // Step 3 → Add product to cart
        //-----------------------------------

        Response addCartResponse =
                ProductAPI.addProductToCart(
                        token,
                        userId,
                        targetProductId,
                        targetProductName
                );

        Assert.assertEquals(
                addCartResponse.statusCode(),
                200
        );

        System.out.println(">>-----------------"+addCartResponse.asString());

        //-----------------------------------
        // Step 4 → Validate cart
        //-----------------------------------

        Response cartResponse =
                CartAPI.getCartProducts(
                        token,
                        userId
                );

        Assert.assertEquals(
                cartResponse.statusCode(),
                200
        );

        String cartProductName =
                cartResponse.jsonPath()
                        .getString("products[0].productName");

        Assert.assertEquals(
                cartProductName,
                targetProductName
        );

        System.out.println(">>-----------------Cart validation passed successfully");
    }
}