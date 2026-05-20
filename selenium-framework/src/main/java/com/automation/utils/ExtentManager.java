package com.automation.utils;

import com.aventstack.extentreports.*;
import com.aventstack.extentreports.reporter.ExtentSparkReporter;

public class ExtentManager {

    private static ExtentReports extent;

    public static ExtentReports getInstance() {

        if (extent == null) {

            ExtentSparkReporter reporter =
                    new ExtentSparkReporter(
                            "target/ExtentReport.html"
                    );

            extent = new ExtentReports();
            extent.attachReporter(reporter);
        }

        return extent;
    }
}