# Selenium Automation Framework

> Production-ready Java test automation framework built with Selenium WebDriver, TestNG, Cucumber BDD, REST Assured, and AI-powered failure analysis integration. Designed to be adapted to any web application with minimal changes.

---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Java | 17 | Core language |
| Selenium WebDriver | 4.x | Browser automation |
| TestNG | 7.x | Test execution and management |
| Cucumber | 7.x | BDD feature file execution |
| REST Assured | 5.x | API automation |
| Maven | 3.8+ | Build and dependency management |
| Apache POI | 5.x | Excel data-driven testing |
| ExtentReports | 5.x | Rich HTML test reports |
| Log4j2 | 2.x | Structured logging |
| Lombok | 1.18.x | Boilerplate reduction |

---

## Folder Structure

```
selenium-framework/
│
├── pom.xml                              ← Maven dependencies and build config
├── testng.xml                           ← TestNG suite configuration and listeners
│
├── .mvn/
│   └── wrapper/
│       ├── maven-wrapper.jar
│       ├── maven-wrapper.properties
│       └── MavenWrapperDownloader.java
│
└── src/
    │
    ├── main/java/com/automation/
    │   │
    │   ├── ai/
    │   │   ├── AIAnalysisService.java   ← Posts failure to AI agent via REST Assured
    │   │
    │   ├── api/
    │   │   ├── LoginAPI.java            ← Login API calls using REST Assured
    │   │   ├── ProductAPI.java          ← Product fetch API calls
    │   │   └── CartAPI.java             ← Cart operations API calls
    │   │
    │   ├── pages/
    │   │   ├── BasePage.java            ← Reusable Selenium actions (click, type, wait)
    │   │   ├── LoginPage.java           ← Login page locators and actions
    │   │   ├── ProductPage.java         ← Product listing locators and actions
    │   │   └── CartPage.java            ← Cart locators and actions
    │   │
    │   └── utils/
    │       ├── DriverFactory.java       ← WebDriver init, teardown, ThreadLocal management
    │       ├── ConfigReader.java        ← Reads config-*.properties by environment
    │       ├── WaitUtils.java           ← Explicit wait helpers
    │       ├── ExtentManager.java       ← Singleton ExtentReports setup
    │       ├── ScreenshotUtil.java      ← Captures screenshot on failure
    │       ├── BrowserLogUtil.java      ← Captures browser console logs
    │       ├── PageSourceUtil.java      ← Captures page source on failure
    │       ├── ExcelUtil.java           ← Apache POI Excel reader
    │       └── ApiUtils.java            ← Shared REST Assured request spec
    │
    └── test/
        ├── java/com/automation/
        │   │
        │   ├── base/
        │   │   ├── BaseTest.java        ← UI test base: driver init, extent setup
        │   │   └── ApiBase.java         ← API test base: base URL, request spec
        │   │
        │   ├── hooks/
        │   │   └── Hooks.java           ← Cucumber @Before (init driver) @After (quit driver)
        │   │
        │   ├── listeners/
        │   │   └── TestListener.java    ← ITestListener: captures failure + calls AI agent
        │   │
        │   ├── retry/
        │   │   └── RetryAnalyzer.java   ← IRetryAnalyzer: retries flaky tests automatically
        │   │
        │   ├── stepdefinitions/
        │   │   └── AddToCartSteps.java  ← Cucumber step definitions for cart feature
        │   │
        │   └── tests/
        │       ├── AddToCartTest.java        ← UI test: login → browse → add to cart
        │       ├── ApiE2ETest.java           ← API E2E: login → products → cart → validate
        │       ├── DataDrivenOrderTest.java  ← Data driven test from Excel
        │       └── TestRunner.java           ← Cucumber TestRunner with feature path
        │
        └── resources/
            ├── config-qa.properties     ← QA environment config
            ├── config-dev.properties    ← Dev environment config
            ├── config-prod.properties   ← Prod environment config
            ├── log4j2.xml               ← Log4j2 logging configuration
            ├── features/
            │   └── addToCart.feature   ← Cucumber BDD feature file
            └── testdata/
                └── LoginTestData.xlsx  ← Excel test data for data-driven tests
```

---

## Framework Features

### UI Automation
- **Page Object Model** — every page has its own class with locators and actions
- **BasePage** — reusable `click()`, `type()`, `getText()`, `waitForVisibility()`, `waitForSpinner()` methods shared across all pages
- **Smart Waits** — explicit waits, spinner waits, visibility waits — no `Thread.sleep()`
- **Screenshot on Failure** — auto-captured via `TestListener.onTestFailure()`

### API Automation
- **REST Assured** based API layer
- Separate API classes: `LoginAPI`, `ProductAPI`, `CartAPI`
- Full E2E API test: login → fetch products → add to cart → validate response
- Shared request specification in `ApiUtils.java`

### BDD Support
- Cucumber feature files written in Gherkin syntax
- Step definitions mapped to reusable page object methods
- `TestRunner.java` for feature file execution with tags

### Data Driven Testing
- Excel-based test data using Apache POI
- TestNG `@DataProvider` integration
- Dynamic test execution — add rows to Excel, no code change needed

### Multi Environment Support
- Separate config files per environment
- `ConfigReader.java` loads correct file based on `env` system property
- Switch environment at runtime via Maven parameter — no code change

### Reliability
- `RetryAnalyzer.java` implements `IRetryAnalyzer`
- Automatically retries failed tests up to configured limit
- Handles flaky tests without manual re-runs

### Reporting
| Report          | Location                      |
|---              |---                            |
| Extent Report   | `target/ExtentReport.html`    |
| Cucumber Report | `target/cucumber-report.html` |
| TestNG Surefire | `target/surefire-reports/`    |

### AI Integration
- `TestListener.java` calls `AIAnalysisService.analyzeFailure()` inside `onTestFailure()`
- `AIAnalysisService.java` POSTs failure details to the Python AI agent via REST Assured
- Zero change to test classes — listener handles everything automatically
- `TestListener` is registered in `testng.xml` as a global listener

### Design Patterns Used
| Pattern | Where |
|---|---|
| Page Object Model | `pages/` package |
| Factory Pattern | `DriverFactory.java` |
| Singleton Pattern | `ExtentManager.java` |
| Data Provider Pattern | `DataDrivenOrderTest.java` |

### SOLID Principles Applied
| Principle | How |
|---|---|
| Single Responsibility | Pages, APIs, utilities, tests are fully separated |
| Open/Closed | Add new tests or environments without changing existing code |
| Liskov Substitution | All page classes safely extend `BasePage` |
| Interface Segregation | `ITestListener`, `IRetryAnalyzer` used only where needed |
| Dependency Inversion | Tests depend on utilities and abstractions, not direct implementations |

---

## Prerequisites

- Java 17
- Maven 3.8+
- Chrome / Firefox / Edge browser installed

---

## Setup and Run

**1. Clone the repository**
```bash
git clone https://github.com/PrakharMittal8/ai-powered-test-automation.git
cd ai-powered-test-automation/selenium-framework
```

**2. Create an account on the test application**

This framework uses a publicly available e-commerce demo web application.
Create your own account and use your own credentials — do not hardcode credentials.

**3. Update credentials**

Edit all 3 config files:
```
src/test/resources/config-qa.properties
src/test/resources/config-dev.properties
src/test/resources/config-prod.properties
```

Update:
```properties
base.url=https://your-application-url.com
username=your_email@example.com
password=your_password
```

Also update `src/test/resources/testdata/LoginTestData.xlsx` with your credentials.

**4. Run tests**

```bash
# Run all tests (default: QA environment)
mvn clean test

# Run specific environment
mvn clean test -Denv=qa
mvn clean test -Denv=dev
mvn clean test -Denv=prod
```

**5. View reports**

Open in browser after test run:
```
target/ExtentReport.html
target/cucumber-report.html
```

---

## How to Adapt to Your Application

This framework is built to be reused. To adapt it to any web application:

| What to change | Where |
|---|---|
| Application URL | `config-*.properties` |
| Login credentials | `config-*.properties` + `LoginTestData.xlsx` |
| Page locators | `pages/` classes |
| API endpoints | `api/` classes |
| Test scenarios | `features/*.feature` files |
| Step definitions | `stepdefinitions/` |
| Test data | `testdata/*.xlsx` |

**What you never need to change:**
`DriverFactory`, `WaitUtils`, `ExtentManager`, `RetryAnalyzer`, `ConfigReader`, `ScreenshotUtil`, `TestListener` — core infrastructure works for any application.

---

## Author

**Prakhar Mittal** — Senior QA Lead
