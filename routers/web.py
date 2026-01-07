from fastapi import APIRouter, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from auth import get_current_active_user
from models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página inicial - redireciona para login"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal - sem autenticação obrigatória"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Página de perfil - sem autenticação obrigatória"""
    return templates.TemplateResponse("profile.html", {"request": request})

@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Painel administrativo - sem autenticação obrigatória"""
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/financeiro", response_class=HTMLResponse)
async def financeiro_page(request: Request):
    """Página do módulo financeiro"""
    return templates.TemplateResponse("financeiro.html", {"request": request})

@router.get("/dashboard-mensal", response_class=HTMLResponse)
async def dashboard_mensal_page(request: Request):
    """Dashboard mensal consolidado"""
    return templates.TemplateResponse("dashboard_mensal.html", {"request": request})

@router.get("/cadastrar-usuario", response_class=HTMLResponse)
async def cadastrar_usuario_page(request: Request):
    """Página de cadastro de usuários"""
    return templates.TemplateResponse("cadastrar_usuario.html", {"request": request})

@router.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """Página de teste do login"""
    with open("test_frontend.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)
