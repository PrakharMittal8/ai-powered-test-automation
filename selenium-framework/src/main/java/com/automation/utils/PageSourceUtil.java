package com.automation.utils;

import org.openqa.selenium.WebDriver;

import java.io.File;
import java.io.FileWriter;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class PageSourceUtil {

    public static String capturePageSource(String testName) {

        try {

            WebDriver driver = DriverFactory.getDriver();

            if (driver == null) {
                return null;
            }

            String pageSource = driver.getPageSource();

            File directory = new File("target/dom");

            if (!directory.exists()) {
                directory.mkdirs();
            }

            String timestamp =
                    LocalDateTime.now()
                            .format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));

            String filePath =
                    "target/dom/" + testName + "_" + timestamp + ".html";

            FileWriter writer = new FileWriter(filePath);

            writer.write(pageSource);

            writer.close();

            return new File(filePath).getAbsolutePath();

        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;
    }
}