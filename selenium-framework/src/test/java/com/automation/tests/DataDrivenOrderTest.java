package com.automation.tests;

import com.automation.base.BaseTest;
import com.automation.pages.*;
import com.automation.retry.RetryAnalyzer;
import com.automation.utils.ExcelUtil;

import org.testng.Assert;
import org.testng.annotations.*;

public class DataDrivenOrderTest extends BaseTest {

    @Test(dataProvider = "orderData", retryAnalyzer = RetryAnalyzer.class)
    public void placeOrderTest(
            String username,
            String password,
            String productName
    ) {

        LoginPage loginPage = new LoginPage(driver);
        ProductPage productPage = new ProductPage(driver);
        CartPage cartPage = new CartPage(driver);

        loginPage.login(username, password);
        productPage.addProductToCart(productName);
        productPage.goToCart();

        Assert.assertTrue(
                cartPage.isProductPresent(productName)
        );
    }

    @DataProvider(name = "orderData")
    public Object[][] getData() {

        return ExcelUtil.getTestData(
                "src/test/resources/testdata/LoginTestData.xlsx",
                "Sheet1"
        );
    }
}