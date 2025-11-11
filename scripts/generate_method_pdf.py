from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import sys
import os

# Ensure project root is on sys.path so we can import app.models
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.models.cost_model import get_form_spec, PRICING

OUTPUT_PATH = "docs/methode_de_calcul.pdf"

def format_dict(d: dict) -> list:
    if isinstance(d, dict):
        return [f"- {k} = {v}" for k, v in d.items()]
    else:
        return [f"- {d}"]

CONTENT = {
    "title": "Méthode de calcul — Estimation coût d'installation d'une Pompe à Chaleur",
    "sections":
    [
        
        {
            "heading": "Pricing — base_m2_ht (€/m² HT)",
            "lines": lambda: format_dict(PRICING.get('base_m2_ht', {})),
        },
        {
            "heading": "Pricing — coef_isolation",
            "lines": lambda: format_dict(PRICING.get('coef_isolation', {})),
        },
        {
            "heading": "Pricing — coef_climat",
            "lines": lambda: format_dict(PRICING.get('coef_climat', {})),
        },
        {
            "heading": "Pricing — coef_logement",
            "lines": lambda: format_dict(PRICING.get('coef_logement', {})),
        },
        {
            "heading": "Pricing — coef_acces_chantier",
            "lines": lambda: format_dict(PRICING.get('coef_acces_chantier', {})),
        },
        {
            "heading": "Pricing — coef_emetteurs",
            "lines": lambda: format_dict(PRICING.get('coef_emetteurs', {})),
        },
        {
            "heading": "Pricing — airair_pieces",
            "lines": lambda: format_dict(PRICING.get('airair_pieces', {})),
        },
        {
            "heading": "Pricing — ECS",
            "lines": lambda: format_dict(PRICING.get('ecs', {})),
        },
        {
            "heading": "Pricing — TVA",
            "lines": lambda: format_dict(PRICING.get('tva', {})),
        },
        {
            "heading": "Formules clés",
            "lines": [
                "surface_corr = surface × coef_isolation × coef_climat",
                "base_ht = surface_corr × base_m2_ht",
                "coef_global = coef_logement × coef_acces_chantier × coef_emetteurs × coef_airair",
                "cout_ht = base_ht × coef_global + cout_ecs_ht",
                "cout_ttc = cout_ht × (1 + tva)",
            ],
        },

    ],
}


def generate_pdf(path: str = OUTPUT_PATH):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    margin = 20 * mm
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, CONTENT["title"])

    y -= 10 * mm

    c.setFont("Helvetica", 10)
    for sec in CONTENT["sections"]:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin, y, sec["heading"])
        y -= 6 * mm
        c.setFont("Helvetica", 10)
        # support lines that are either static lists or callables returning a list
        lines = sec.get("lines", [])
        if callable(lines):
            try:
                lines = lines()
            except Exception:
                lines = ["(impossible de charger ces lignes)"]
        for line in lines:
            # wrap manually if too long
            max_width = width - 2 * margin
            text = line
            # simple wrap by splitting words
            words = text.split(' ')
            line_buf = ''
            for w in words:
                if c.stringWidth(line_buf + ' ' + w, "Helvetica", 10) < max_width:
                    if line_buf:
                        line_buf += ' ' + w
                    else:
                        line_buf = w
                else:
                    c.drawString(margin + 4*mm, y, line_buf)
                    y -= 5 * mm
                    line_buf = w
                    if y < margin:
                        c.showPage()
                        y = height - margin
            if line_buf:
                c.drawString(margin + 4*mm, y, line_buf)
                y -= 5 * mm
            y -= 1 * mm
        y -= 4 * mm
        if y < margin:
            c.showPage()
            y = height - margin

    c.showPage()
    c.save()


if __name__ == '__main__':
    import os

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    generate_pdf()
    print(f"PDF généré : {OUTPUT_PATH}")
