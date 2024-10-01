from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import cv2  # Para captura de imagens (opcional)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Simulação de estoque e temperatura
stock = {}
temperature_logs = []
recipes = {
    "Salada": ["Tomato", "Lettuce", "Olive Oil"],
    "Omelete": ["Egg", "Cheese", "Ham"],
    "Smoothie": ["Milk", "Banana", "Honey"]
}

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Adicionar produto ao estoque via formulário
@app.get("/add_item_form", response_class=HTMLResponse)
def add_item_form_page(request: Request):
    return templates.TemplateResponse("add_item_form.html", {"request": request})

@app.post("/add_item_form")
def add_item_form(name: str = Form(...), quantity: int = Form(...), expiration_date: str = Form(...)):
    expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
    stock[name] = {"quantity": quantity, "expiration_date": expiration_date}
    return RedirectResponse(url="/", status_code=303)

# Gestão do Estoque: Verificar estoque
@app.get("/stock", response_class=HTMLResponse)
def get_stock(request: Request):
    return templates.TemplateResponse("stock.html", {"request": request, "stock": stock})

# Controle de Temperatura: Ajustar temperatura e monitorar
@app.get("/temperature", response_class=HTMLResponse)
def get_temperature_logs(request: Request):
    return templates.TemplateResponse("temperature.html", {"request": request, "logs": temperature_logs})

@app.post("/set_temperature_form")
def set_temperature_form(temperature: float = Form(...)):
    if temperature < 0 or temperature > 10:
        return {"message": "Temperatura fora do limite seguro (0-10°C)."}
    log = {"timestamp": datetime.now(), "temperature": temperature}
    temperature_logs.append(log)
    return RedirectResponse(url="/temperature", status_code=303)

# Monitoramento do Prazo de Validade
@app.get("/expired_items", response_class=HTMLResponse)
def check_expired_items(request: Request):
    current_date = datetime.now().date()
    expired_items = [item for item, details in stock.items() if details["expiration_date"].date() < current_date]
    return templates.TemplateResponse("expired_items.html", {"request": request, "expired_items": expired_items})

# Recomendação de Receitas
@app.get("/recipes", response_class=HTMLResponse)
def recommend_recipe(request: Request):
    available_items = [item for item in stock]
    recommended = [recipe for recipe, ingredients in recipes.items() if all(ingredient in available_items for ingredient in ingredients)]
    return templates.TemplateResponse("recipes.html", {"request": request, "recommended": recommended})

# Funcionalidade de Câmera: Captura de Imagem
@app.get("/capture_image", response_class=HTMLResponse)
def capture_image(request: Request):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("static/captured_image.jpg", frame)
        cap.release()
        return templates.TemplateResponse("camera.html", {"request": request, "image": "/static/captured_image.jpg"})
    cap.release()
    return templates.TemplateResponse("camera.html", {"request": request, "image": None})

