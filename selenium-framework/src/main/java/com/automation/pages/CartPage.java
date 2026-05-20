package com.automation.pages;

import org.openqa.selenium.*;
import java.util.List;

public class CartPage extends BasePage {

    public CartPage(WebDriver driver) {
        super(driver);
    }

    private By cartItems = By.cssSelector(".infoWrap");

    public boolean isProductPresent(String productName) {

        List<WebElement> items = driver.findElements(cartItems);

        for (WebElement item : items) {
            if (item.getText().contains(productName)) {
                return true;
            }
        }

        return false;
    }
}