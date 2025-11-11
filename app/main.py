from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.models.cost_model import CostModel, InputParams, get_form_spec, PRICING

app = FastAPI(title="Thermocost", version="0.1.0")

# Templates
templates = Jinja2Templates(directory="app/templates")


def build_defaults(fields):
    defaults = {}
    for f in fields:
        fid = f.get('id')
        ftype = f.get('type')
        if ftype == 'select':
            opts = f.get('options', [])
            defaults[fid] = opts[0] if opts else ''
        elif ftype == 'number':
            # Leave number fields empty so user enters their own value
            defaults[fid] = ''
        elif ftype == 'boolean':
            defaults[fid] = False
        else:
            defaults[fid] = ''
    return defaults


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    fields = get_form_spec()
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "errors": None, "fields": fields, "defaults": build_defaults(fields), "currency": PRICING.get('currency', 'EUR')})


@app.post("/estimate", response_class=HTMLResponse)
async def estimate(request: Request):
    fields = get_form_spec()
    form = await request.form()

    # build params dict
    data = {}
    for f in fields:
        fid = f['id']
        ftype = f.get('type')
        required = f.get('required', False)
        
        if ftype == 'boolean':
            # checkbox: present in form if checked
            data[fid] = fid in form
        else:
            val = form.get(fid)
            # Pour les champs optionnels non remplis, passer None (Pydantic les ignorera si default est défini)
            if val is None and not required:
                # Pour les nombres optionnels, on peut passer 0 ou None; pour les strings optionnelles, on passe None
                data[fid] = None
            else:
                data[fid] = val

    try:
        params = InputParams(**data)
        result = CostModel.estimate(params)
        # prepare defaults from submitted
        submitted_defaults = {k: (getattr(params, k) if hasattr(params, k) else None) for k in [f['id'] for f in fields]}
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "result": result, "errors": None, "fields": fields, "defaults": submitted_defaults, "currency": PRICING.get('currency', 'EUR')},
        )
    except ValidationError as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "result": None, "errors": e.errors(), "fields": fields, "defaults": build_defaults(fields), "currency": PRICING.get('currency', 'EUR')},
        )


@app.post("/api/estimate")
async def api_estimate(params: InputParams):
    return CostModel.estimate(params)
