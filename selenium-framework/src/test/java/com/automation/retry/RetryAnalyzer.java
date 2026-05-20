package com.automation.retry;

import org.testng.IRetryAnalyzer;
import org.testng.ITestResult;

public class RetryAnalyzer implements IRetryAnalyzer {

    private int count = 0;
    private int maxRetry = 0;

    @Override
    public boolean retry(ITestResult result) {

        if (count < maxRetry) {
            count++;
            return true;
        }

        return false;
    }
}
