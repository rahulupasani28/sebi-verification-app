from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from starlette.middleware.sessions import SessionMiddleware
from passlib.hash import bcrypt
from models import SessionLocal, Advisor, User

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request):
    return request.session.get("user")
#--------LOGIN-----------
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.verify(password, user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user"] = user.username
    response = RedirectResponse("/manage", status_code=303)
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    response = RedirectResponse("/login", status_code=303)
    response.headers["Cache-Control"] = "no-store"
    return response

# ----------------LOGIN END----------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/verify", response_class=HTMLResponse)
async def verify_form(request: Request, sebi_reg_no: str = Form(...), db: Session = Depends(get_db)):
    advisor = db.query(Advisor).filter(
        func.trim(func.lower(Advisor.sebi_reg_no)) == sebi_reg_no.strip().lower()
    ).first()
    if not advisor:
        result = {"error": "Advisor not found"}
    else:
        result = {"sebi_reg_no": advisor.sebi_reg_no.strip(), "name": advisor.name.strip()}
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

@app.get("/verify/{sebi_reg_no}")
async def verify_advisor(sebi_reg_no: str, db: Session = Depends(get_db)):
    advisor = db.query(Advisor).filter(
        func.trim(func.lower(Advisor.sebi_reg_no)) == sebi_reg_no.strip().lower()
    ).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")
    return {"sebi_reg_no": advisor.sebi_reg_no.strip(), "name": advisor.name.strip()}

@app.get("/manage", response_class=HTMLResponse)
async def manage_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    advisors = db.query(Advisor).all()
    response = templates.TemplateResponse("manage.html", {"request": request, "advisors": advisors, "user": user})
    response.headers["Cache-Control"] = "no-store"
    return response

@app.post("/manage/add")
async def add_advisor(request: Request, sebi_reg_no: str = Form(...), name: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    existing = db.query(Advisor).filter(Advisor.sebi_reg_no == sebi_reg_no.strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Advisor already exists")
    advisor = Advisor(sebi_reg_no=sebi_reg_no.strip(), name=name.strip())
    db.add(advisor)
    db.commit()
    response = RedirectResponse("/manage", status_code=303)
    response.headers["Cache-Control"] = "no-store"
    return response

@app.post("/manage/delete")
async def delete_advisor(request: Request, sebi_reg_no: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    advisor = db.query(Advisor).filter(Advisor.sebi_reg_no == sebi_reg_no.strip()).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Advisor not found")
    db.delete(advisor)
    db.commit()
    response = RedirectResponse("/manage", status_code=303)
    response.headers["Cache-Control"] = "no-store"
    return response
