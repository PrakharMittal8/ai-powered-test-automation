package com.automation.api;

import com.automation.utils.ApiUtils;
import io.restassured.response.Response;

public class CartAPI {

    public static Response getCartProducts(
            String token,
            String userId
    ) {

        return ApiUtils.getRequestSpec(token)
                .when()
                .get("/api/ecom/user/get-cart-products/" + userId);
    }
}
