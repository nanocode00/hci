from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from db import SessionLocal, Report, Stock, Broker, Author

app = FastAPI()

# 1. Static directory mount
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Jinja2 Templates configuration
templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "query": q}

# 3. Routes serving Jinja2 templates

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/index.html", response_class=HTMLResponse)
async def read_index_alias(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/card.html", response_class=HTMLResponse)
async def read_card(request: Request):
    return templates.TemplateResponse("card.html", {"request": request})

@app.get("/data.html", response_class=HTMLResponse)
async def read_data(request: Request, q: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Report).join(Report.stock).outerjoin(Report.broker).outerjoin(Report.author)
    
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Stock.stock_name.like(search_term),
                Broker.name.like(search_term),
                Author.name.like(search_term)
            )
        )
    
    reports = query.order_by(Report.written_date.desc()).all()
    
    return templates.TemplateResponse("data.html", {"request": request, "reports": reports, "q": q})

@app.get("/statistic.html", response_class=HTMLResponse)
async def read_statistic(request: Request):
    return templates.TemplateResponse("statistic.html", {"request": request})

@app.get("/signin.html", response_class=HTMLResponse)
async def read_signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@app.get("/register.html", response_class=HTMLResponse)
async def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/forgotpw.html", response_class=HTMLResponse)
async def read_forgotpw(request: Request):
    return templates.TemplateResponse("forgotpw.html", {"request": request})

@app.get("/tmp.html", response_class=HTMLResponse)
async def read_tmp(request: Request):
    return templates.TemplateResponse("tmp.html", {"request": request})

#uvicorn main:app --reload
