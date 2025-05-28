from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
import uvicorn
from pathlib import Path
from typing import Optional

app = FastAPI()

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['court_documents']
issues_collection = db['issues']

# Create and mount static directory
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Create templates directory if it doesn't exist
Path("templates").mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, show_all: bool = False):
    results = []
    if show_all:
        results = list(issues_collection.find({}))
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "results": results,
        "show_all": show_all
    })

@app.post("/", response_class=HTMLResponse)
async def search(
    request: Request, 
    show_all: bool = Form(False),
    query: Optional[str] = Form(None)
):
    results = []
    if show_all:
        results = list(issues_collection.find({}))
    elif query:
        # Search in multiple fields
        results = list(issues_collection.find({
            "$or": [
                {"Case_number": {"$regex": query, "$options": "i"}},
                {"Plaintiff_name": {"$regex": query, "$options": "i"}},
                {"defendant_names": {"$regex": query, "$options": "i"}},
                {"table_name": {"$regex": query, "$options": "i"}},
                {"judgment_or_decision_info": {"$regex": query, "$options": "i"}},
                {"Previous_session_infos": {"$regex": query, "$options": "i"}}
            ]
        }))
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "results": results, "query": query, "show_all": show_all}
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True) 