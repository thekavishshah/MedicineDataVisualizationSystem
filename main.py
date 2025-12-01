from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routers import insights, medicines
import os

app = FastAPI()

frontend_path = os.path.join(os.path.dirname(__file__), "frontend")

app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")

@app.get("/")
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

app.include_router(insights.router)
app.include_router(medicines.router, prefix="/api/medicines")
