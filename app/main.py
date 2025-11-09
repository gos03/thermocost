from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError


from app.models.cost_model import CostModel, InputParams


app = FastAPI(title="Thermocost", version="0.1.0")


# Templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "errors": None})


@app.post("/estimate", response_class=HTMLResponse)
async def estimate(
    request: Request,
    surface_m2: float = Form(...),
    insulation: str = Form(...),
    climate: str = Form(...),
    hp_type: str = Form(...),
    emitters: str = Form(...),
    complexity: str = Form("standard"),
    needs_dhw: bool = Form(False),
    brand: str = Form("milieu_de_gamme"),

):
    try:
        params = InputParams(
            surface_m2=surface_m2,
            insulation=insulation,
            climate=climate,
            hp_type=hp_type,
            emitters=emitters,
            complexity=complexity,
            needs_dhw=needs_dhw,
            brand=brand,
        )
        result = CostModel.estimate(params)
        return templates.TemplateResponse("index.html", {"request": request, "result": result, "errors": None})
    except ValidationError as e:
        return templates.TemplateResponse("index.html", {"request": request, "result": None, "errors": e.errors()})


@app.post("/api/estimate")
async def api_estimate(params: InputParams):
    return CostModel.estimate(params)