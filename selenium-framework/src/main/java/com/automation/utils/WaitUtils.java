package com.automation.utils;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.*;

import java.time.Duration;

public class WaitUtils {

    public static void waitForElementVisible(WebDriver driver, By locator) {

        WebDriverWait wait = new WebDriverWait(
                driver,
                Duration.ofSeconds(
                        Integer.parseInt(ConfigReader.get("explicitWait"))
                )
        );

        wait.until(
                ExpectedConditions.visibilityOfElementLocated(locator)
        );
    }

    public static void waitForAllElementsVisible(WebDriver driver, By locator) {

        WebDriverWait wait = new WebDriverWait(
                driver,
                Duration.ofSeconds(
                        Integer.parseInt(ConfigReader.get("explicitWait"))
                )
        );

        wait.until(
                ExpectedConditions.visibilityOfAllElementsLocatedBy(locator)
        );
    }

    public static void waitForElementClickable(WebDriver driver, WebElement element) {

        WebDriverWait wait = new WebDriverWait(
                driver,
                Duration.ofSeconds(
                        Integer.parseInt(ConfigReader.get("explicitWait"))
                )
        );

        wait.until(
                ExpectedConditions.elementToBeClickable(element)
        );
}

       // wait.until(ExpectedConditions.invisibilityOf(driver.findElement(By.cssSelector(".ng-animating"))));
	
      public static void waitForInvisibilityOfElement(WebDriver driver, By locator) {
 WebDriverWait wait = new WebDriverWait(
 driver,
 Duration.ofSeconds(
 Integer.parseInt(ConfigReader.get("explicitWait"))
 )
 );

 try {
 wait.until(
 ExpectedConditions.invisibilityOfElementLocated(locator)
 );
 } catch (Exception e) {
 System.out.println("Spinner not found or already disappeared");
 }
}
}