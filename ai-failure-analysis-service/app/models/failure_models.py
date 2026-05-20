from pydantic import BaseModel


class FailureRequest(BaseModel):
    testName: str
    exceptionMessage: str
    stackTrace: str
    screenshotPath: str
    pageSourcePath: str
    browserLogs: str
    timestamp: str
    environment: str