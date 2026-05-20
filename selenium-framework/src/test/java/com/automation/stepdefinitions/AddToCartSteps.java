package com.automation.stepdefinitions;

import com.automation.pages.CartPage;
import com.automation.pages.LoginPage;
import com.automation.pages.ProductPage;
import com.automation.utils.ConfigReader;
import com.automation.utils.DriverFactory;

import io.cucumber.java.en.*;

import org.openqa.selenium.WebDriver;
import org.testng.Assert;

public class AddToCartSteps {

    WebDriver driver = DriverFactory.getDriver();

    LoginPage loginPage;
    ProductPage productPage;
    CartPage cartPage;

    @Given("user launches application")
    public void user_launches_application() {

        driver.get(ConfigReader.get("baseUrl"));

        loginPage = new LoginPage(driver);
        productPage = new ProductPage(driver);
        cartPage = new CartPage(driver);
    }

    @When("user logs in with valid credentials")
    public void user_logs_in_with_valid_credentials() {

        loginPage.login(
                ConfigReader.get("username"),
                ConfigReader.get("password")
        );
    }

    @When("user adds product {string} to cart")
    public void user_adds_product_to_cart(String productName) throws InterruptedException {

        productPage.addProductToCart(productName);
        
    }

    @When("user navigates to cart page")
    public void user_navigates_to_cart_page() {

        productPage.goToCart();
    }

    @Then("product {string} should be visible in cart")
    public void product_should_be_visible_in_cart(String productName) {

        Assert.assertTrue(
                cartPage.isProductPresent(productName)
        );
    }
}
