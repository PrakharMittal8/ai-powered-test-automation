package com.automation.utils;

import org.apache.commons.io.FileUtils;
import org.openqa.selenium.*;

import java.io.File;

public class ScreenshotUtil {

    public static String capture(String testName) {

        try {

            WebDriver driver = DriverFactory.getDriver();

            // API tests won't have browser session
            if (driver == null) {
                System.out.println("No browser session found. Screenshot skipped.");
                return null;
            }

            TakesScreenshot ts = (TakesScreenshot) driver;

            File src = ts.getScreenshotAs(OutputType.FILE);

            File dest = new File(
                    "target/screenshots/" + testName + ".png"
            );

            FileUtils.copyFile(src, dest);

            return dest.getAbsolutePath();

        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;
    }
}