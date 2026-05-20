package com.automation.utils;

import io.github.bonigarcia.wdm.WebDriverManager;

import org.openqa.selenium.WebDriver;

import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;

import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;

import org.openqa.selenium.logging.LogType;
import org.openqa.selenium.logging.LoggingPreferences;

import org.openqa.selenium.remote.RemoteWebDriver;

import java.time.Duration;
import java.util.logging.Level;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class DriverFactory {

    private static final Logger log =
            LogManager.getLogger(DriverFactory.class);

    private static ThreadLocal<WebDriver> driver =
            new ThreadLocal<>();

    public static void initDriver() {

        String browser = ConfigReader.get("browser");
        String headless = ConfigReader.get("headless");
        String runMode = ConfigReader.get("runMode");

        log.info("Run Mode: " + runMode);
        log.info("Browser: " + browser);

        WebDriver webDriver = null;

        try {

            //------------------------------------------
            // CHROME
            //------------------------------------------

            if (browser.equalsIgnoreCase("chrome")) {

                ChromeOptions options = new ChromeOptions();

                //------------------------------------------
                // ENABLE BROWSER LOGGING
                //------------------------------------------

                LoggingPreferences logs =
                        new LoggingPreferences();

                logs.enable(
                        LogType.BROWSER,
                        Level.ALL
                );

                options.setCapability(
                        "goog:loggingPrefs",
                        logs
                );

                //------------------------------------------
                // CHROME OPTIONS
                //------------------------------------------

                options.addArguments("--start-maximized");
                options.addArguments("--disable-notifications");

                if (headless.equalsIgnoreCase("true")) {
                    options.addArguments("--headless=new");
                }

                //------------------------------------------
                // REMOTE EXECUTION
                //------------------------------------------

                if (runMode.equalsIgnoreCase("remote")) {

                    log.info("Starting Remote ChromeDriver");

                    webDriver =
                            new RemoteWebDriver(
                                    new java.net.URI(
                                            ConfigReader.get("gridUrl")
                                    ).toURL(),
                                    options
                            );

                }

                //------------------------------------------
                // LOCAL EXECUTION
                //------------------------------------------

                else {

                    log.info("Starting Local ChromeDriver");

                    WebDriverManager.chromedriver().setup();

                    webDriver =
                            new ChromeDriver(options);
                }
            }

            //------------------------------------------
            // FIREFOX
            //------------------------------------------

            else if (browser.equalsIgnoreCase("firefox")) {

                FirefoxOptions options =
                        new FirefoxOptions();

                if (headless.equalsIgnoreCase("true")) {
                    options.addArguments("--headless");
                }

                if (runMode.equalsIgnoreCase("remote")) {

                    log.info("Starting Remote FirefoxDriver");

                    webDriver =
                            new RemoteWebDriver(
                                    new java.net.URI(
                                            ConfigReader.get("gridUrl")
                                    ).toURL(),
                                    options
                            );

                } else {

                    log.info("Starting Local FirefoxDriver");

                    WebDriverManager.firefoxdriver().setup();

                    webDriver =
                            new FirefoxDriver(options);
                }
            }

            //------------------------------------------
            // EDGE
            //------------------------------------------

            else if (browser.equalsIgnoreCase("edge")) {

                EdgeOptions options =
                        new EdgeOptions();

                if (runMode.equalsIgnoreCase("remote")) {

                    log.info("Starting Remote EdgeDriver");

                    webDriver =
                            new RemoteWebDriver(
                                    new java.net.URI(
                                            ConfigReader.get("gridUrl")
                                    ).toURL(),
                                    options
                            );

                } else {

                    log.info("Starting Local EdgeDriver");

                    WebDriverManager.edgedriver().setup();

                    webDriver =
                            new EdgeDriver(options);
                }
            }

            //------------------------------------------
            // INVALID BROWSER
            //------------------------------------------

            else {

                throw new RuntimeException(
                        "Invalid browser: " + browser
                );
            }

        }

        catch (Exception e) {

            throw new RuntimeException(
                    "Driver initialization failed: "
                            + e.getMessage()
            );
        }

        //------------------------------------------
        // THREADLOCAL SET
        //------------------------------------------

        driver.set(webDriver);

        log.info("Driver initialized successfully");

        //------------------------------------------
        // IMPLICIT WAIT
        //------------------------------------------

        getDriver().manage().timeouts().implicitlyWait(
                Duration.ofSeconds(
                        Integer.parseInt(
                                ConfigReader.get("implicitWait")
                        )
                )
        );
    }

    //------------------------------------------
    // GET DRIVER
    //------------------------------------------

    public static WebDriver getDriver() {
        return driver.get();
    }

    //------------------------------------------
    // QUIT DRIVER
    //------------------------------------------

    public static void quitDriver() {

        if (driver.get() != null) {

            log.info("Closing browser");

            driver.get().quit();

            driver.remove();
        }
    }
}