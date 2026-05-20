package com.automation.utils;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.logging.LogEntries;
import org.openqa.selenium.logging.LogEntry;

public class BrowserLogUtil {

    public static String captureBrowserLogs() {

        try {

            WebDriver driver = DriverFactory.getDriver();

            if (driver == null) {
                return "No browser session available";
            }

            LogEntries logs =
                    driver.manage()
                            .logs()
                            .get("browser");

            StringBuilder builder = new StringBuilder();

            for (LogEntry entry : logs) {

                builder.append(entry.getLevel())
                        .append(" : ")
                        .append(entry.getMessage())
                        .append("\n");
            }

            return builder.toString();

        } catch (Exception e) {

            return "Failed to capture browser logs: " + e.getMessage();
        }
    }
}