package com.automation.api;

import com.automation.utils.ApiUtils;
import io.restassured.response.Response;
import org.json.JSONArray;
import org.json.JSONObject;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class ProductAPI {

    private static final Logger log =
        LogManager.getLogger(ProductAPI.class);
    public static Response getAllProducts(String token) {

        JSONObject requestBody = new JSONObject();

        requestBody.put("productName", "");
        requestBody.put("minPrice", JSONObject.NULL);
        requestBody.put("maxPrice", JSONObject.NULL);
        requestBody.put("productCategory", new JSONArray());
        requestBody.put("productSubCategory", new JSONArray());
        requestBody.put("productFor", new JSONArray());
        log.info("Fetching all products");

        Response response = ApiUtils.getRequestSpec(token)
                .body(requestBody.toString())
                .when()
                .post("/api/ecom/product/get-all-products");
        log.info("Products API Response: " + response.asString());
        
        return response;
    }

    public static Response addProductToCart(
            String token,
            String userId,
            String productId,
            String productName
    ) {

        JSONObject productObject = new JSONObject();
        productObject.put("_id", productId);
        productObject.put("productName", productName);

        JSONObject requestBody = new JSONObject();
        requestBody.put("_id", userId);
        requestBody.put("product", productObject);

        log.info("Adding product to cart: " + productName);

        Response response = ApiUtils.getRequestSpec(token)
                .body(requestBody.toString())
                .when()
                .post("/api/ecom/user/add-to-cart");

        log.info("Add to cart response: " + response.asString());

        return response;
    }
}