package com.automation.pages;

import com.automation.utils.WaitUtils;
import org.openqa.selenium.*;

import java.util.List;

public class ProductPage extends BasePage {

    public ProductPage(WebDriver driver) {
        super(driver);
    }

    private By products = By.cssSelector(".mb-3");
    private By cartBtn = By.xpath("//button[@routerlink='/dashboard/cart']");

    //Wrong Locator for Testing AI RCA Response
   // private By cartBtn = By.xpath("//butto[@routerlink='/dashboard/cart']");
   
    private By spinner = By.cssSelector(".ng-animating");

    public void addProductToCart(String productName){

        WaitUtils.waitForAllElementsVisible(driver, products);

        List<WebElement> items = driver.findElements(products);

        for (WebElement product : items) {

            String name =
                    product.findElement(By.tagName("b")).getText();

            if (name.equalsIgnoreCase(productName)) {

                WebElement addButton =
                        product.findElement(By.xpath(".//button[2]"));

                WaitUtils.waitForElementClickable(driver, addButton);

                addButton.click();

                WaitUtils.waitForInvisibilityOfElement(driver, spinner);
                
                break;
            }
        }
    }

    public void goToCart() {
        click(cartBtn);
    }
}