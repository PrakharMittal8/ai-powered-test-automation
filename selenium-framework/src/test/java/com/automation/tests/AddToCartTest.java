package com.automation.tests;

import com.automation.base.BaseTest;
import com.automation.pages.*;
import com.automation.retry.RetryAnalyzer;
import com.automation.utils.ConfigReader;

import org.testng.Assert;
import org.testng.annotations.Test;

public class AddToCartTest extends BaseTest {

    //Upgrade: Introduce "Annotation transformer"
    //1. to avoid writing RetryAnalyzer in each test manually.
    //2. to enable/disable certain tests without touching code file.

    @Test(retryAnalyzer = RetryAnalyzer.class)
    public void addProductToCartTest() throws InterruptedException {

        LoginPage loginPage = new LoginPage(driver);
        ProductPage productPage = new ProductPage(driver);
        CartPage cartPage = new CartPage(driver);

        loginPage.login(
                ConfigReader.get("username"),
                ConfigReader.get("password")
        );

        productPage.addProductToCart("ZARA COAT 3");
       Thread.sleep(2000);
        productPage.goToCart();

        Assert.assertTrue(
                cartPage.isProductPresent("ZARA COAT 3")
        );
    }

     @Test(retryAnalyzer = RetryAnalyzer.class, enabled = false)
    public void addProductTest() throws InterruptedException {

        LoginPage loginPage = new LoginPage(driver);
        ProductPage productPage = new ProductPage(driver);
        CartPage cartPage = new CartPage(driver);

        loginPage.login(
                ConfigReader.get("username"),
                ConfigReader.get("password")
        );

        productPage.addProductToCart("ZARA COAT 3");
       Thread.sleep(2000);
        productPage.goToCart();

        Assert.assertTrue(
                cartPage.isProductPresent("ZARA COAT 2")
        );
    }
}
