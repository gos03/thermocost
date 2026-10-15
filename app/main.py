from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

import importlib
from pathlib import Path

import app.models.cost_model as cost_model

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
            defaults[fid] = f.get('default', '')
        elif ftype == 'boolean':
            defaults[fid] = False
        else:
            defaults[fid] = ''
    return defaults


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    fields = cost_model.get_form_spec()
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "errors": None, "fields": fields, "defaults": build_defaults(fields), "currency": getattr(cost_model, 'CURRENCY', 'EUR')})


@app.post("/estimate", response_class=HTMLResponse)
async def estimate(request: Request):
    fields = cost_model.get_form_spec()
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
        params = cost_model.InputParams(**data)
        result = cost_model.CostModel.estimate(params)
        # prepare defaults from submitted
        submitted_defaults = {k: (getattr(params, k) if hasattr(params, k) else None) for k in [f['id'] for f in fields]}
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "result": result, "errors": None, "fields": fields, "defaults": submitted_defaults, "currency": getattr(cost_model, 'CURRENCY', 'EUR')},
        )
    except ValidationError as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "result": None, "errors": e.errors(), "fields": fields, "defaults": build_defaults(fields), "currency": getattr(cost_model, 'CURRENCY', 'EUR')},
        )


@app.post("/api/estimate")
async def api_estimate(params: cost_model.InputParams):
    return cost_model.CostModel.estimate(params)


@app.get('/config', response_class=HTMLResponse)
async def config_get(request: Request):
    # show access form
    return templates.TemplateResponse('config.html', {"request": request, "step": "login", "message": None})


@app.post('/config', response_class=HTMLResponse)
async def config_post(request: Request):
    form = await request.form()
    code = form.get('code', '')
    action = form.get('action', 'login')
    CONFIG_PATH = Path(__file__).parent / 'models' / 'cost_model.json'

    if code != 'jeanmarc':
        return templates.TemplateResponse('config.html', {"request": request, "step": "login", "message": "Code incorrect"})

    if action == 'login':
        # show editor with current JSON
        try:
            text = CONFIG_PATH.read_text(encoding='utf-8')
        except Exception:
            text = ''
        return templates.TemplateResponse('config.html', {"request": request, "step": "edit", "json_text": text, "message": None})

    if action == 'save':
        json_text = form.get('json_content', '')
        # validate JSON
        try:
            parsed = __import__('json').loads(json_text)
        except Exception as e:
            return templates.TemplateResponse('config.html', {"request": request, "step": "edit", "json_text": json_text, "message": f"JSON invalide: {e}"})
        # write file
        try:
            CONFIG_PATH.write_text(__import__('json').dumps(parsed, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            return templates.TemplateResponse('config.html', {"request": request, "step": "edit", "json_text": json_text, "message": f"Erreur écriture: {e}"})
        # reload module
        try:
            importlib.reload(cost_model)
        except Exception as e:
            return templates.TemplateResponse('config.html', {"request": request, "step": "edit", "json_text": json_text, "message": f"Erreur reload module: {e}"})

        return templates.TemplateResponse('config.html', {"request": request, "step": "edit", "json_text": json_text, "message": "Fichier sauvegardé et module rechargé."})
