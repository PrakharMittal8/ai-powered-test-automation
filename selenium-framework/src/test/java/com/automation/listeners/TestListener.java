package com.automation.listeners;
import com.automation.utils.*;
import com.aventstack.extentreports.*;
import org.testng.*;
import com.automation.ai.AIAnalysisService;

//mport com.automation.ai.AIAnalysisService;
//import com.automation.ai.models.FailureContext;
//import com.automation.ai.orchestrator.AIOrchestrator;

//import java.time.LocalDateTime;

public class TestListener implements ITestListener {

    private static ExtentReports extent =
            ExtentManager.getInstance();

    private static ThreadLocal<ExtentTest> extentTest =
            new ThreadLocal<>();

    @Override
    public void onTestStart(ITestResult result) {
        ExtentTest test =
                extent.createTest(
                        result.getMethod().getMethodName()
                );
        extentTest.set(test);
    }

    @Override
    public void onTestSuccess(ITestResult result) {
        extentTest.get().pass("Test Passed");
        
    }

    @Override
public void onTestFailure(ITestResult result) {

    extentTest.get().fail(result.getThrowable());

    String screenshotPath =
            ScreenshotUtil.capture(
                    result.getName()
            );

    String pageSourcePath =
            PageSourceUtil.capturePageSource(
                    result.getName()
            );

    String browserLogs =
            BrowserLogUtil.captureBrowserLogs();

    try {

        String aiResponse =
                AIAnalysisService.analyzeFailure(
                        result.getName(),
                        result.getThrowable().getMessage(),
                        result.getThrowable().toString(),
                        screenshotPath,
                        pageSourcePath,
                        browserLogs,
                        java.time.LocalDateTime.now().toString(),
                        System.getProperty("env", "qa")
                );

        System.out.println("\n================ AI RCA RESPONSE ================\n");
        System.out.println(aiResponse);
        System.out.println("\n=================================================\n");

    } catch (Exception e) {

        System.out.println("AI Analysis Failed: " + e.getMessage());
    }

    try {

        if (screenshotPath != null) {

            extentTest.get()
                    .addScreenCaptureFromPath(screenshotPath);
        }

    } catch (Exception e) {
        e.printStackTrace();
    }
}

    @Override
    public void onFinish(ITestContext context) {
        extent.flush();
    }
}
