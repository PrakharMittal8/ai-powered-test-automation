from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from app.routes.analysis_routes import router
from app.services.dashboard_service import DashboardService

app = FastAPI(title="AI Failure Analysis Service")
dashboard_service = DashboardService()

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/dashboard-data")
def dashboard_data():
    return JSONResponse(content=dashboard_service.get_all())


@app.get("/dashboard")
def dashboard():
    return FileResponse("dashboard/index.html")