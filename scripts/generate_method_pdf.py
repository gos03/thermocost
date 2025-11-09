from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import sys
import os

# Ensure project root is on sys.path so we can import app.models
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.models.cost_model import (
    INSULATION_W_PER_M2,
    CLIMATE_MULTIPLIER,
    BASE_COST_PER_KW,
    EMITTERS_FACTOR,
    COMPLEXITY_FACTOR,
    BRAND_PREMIUM,
    DHW_COST_BY_TYPE,
    AUX_FLAT_COSTS,
)

OUTPUT_PATH = "docs/methode_de_calcul.pdf"

def format_dict(d: dict) -> list:
    return [f"- {k} = {v}" for k, v in d.items()]

CONTENT = {
    "title": "Méthode de calcul — Estimation coût Pompe à Chaleur",
    "sections": [
        {
            "heading": "1) Données d'entrée",
            "lines": [
                "- surface_m2 : surface chauffée en m² (ex : 120)",
                "- insulation : niveau d'isolation (très_bon, bon, moyen, mauvais)",
                "- climate : zone climatique (doux, tempéré, froid)",
                "- hp_type : type de pompe (air_air, air_eau, geothermie)",
                "- emitters : type d'émetteurs (radiateurs_basse_t, radiateurs_haut_t, plancher_chauffant)",
                "- complexity : complexité du chantier (simple, standard, complexe)",
                "- needs_dhw : besoin d'ECS (True/False)",
                "- brand : gamme (entrée_de_gamme, milieu_de_gamme, premium)",
            ],
        },
        {
            "heading": "Constantes — Déperditions par isolation (W/m²)",
            "lines": format_dict(INSULATION_W_PER_M2),
        },
        {
            "heading": "Constantes — Facteurs climatiques",
            "lines": format_dict(CLIMATE_MULTIPLIER),
        },
        {
            "heading": "Constantes — Coût unitaire par kW (€/kW)",
            "lines": format_dict(BASE_COST_PER_KW),
        },
        {
            "heading": "Constantes — Facteurs émetteurs",
            "lines": format_dict(EMITTERS_FACTOR),
        },
        {
            "heading": "Constantes — Facteurs complexité",
            "lines": format_dict(COMPLEXITY_FACTOR),
        },
        {
            "heading": "Constantes — Prime de marque",
            "lines": format_dict(BRAND_PREMIUM),
        },
        {
            "heading": "Constantes — Coûts ECS par type",
            "lines": format_dict(DHW_COST_BY_TYPE),
        },
        {
            "heading": "Constantes — Coûts auxiliaires fixes",
            "lines": format_dict(AUX_FLAT_COSTS),
        },
        {
            "heading": "Formules clés",
            "lines": [
                "Puissance (kW) = (surface_m2 × déperdition_specifique (W/m²) × facteur_climatique × 1.10) / 1000",
                "Coût de base (EUR) = required_kW × coût_unitaire_par_kW",
                "Coût ajusté = coût de base × facteur_émetteurs × facteur_complexité × prime_marque",
                "Total = coût ajusté + somme(coûts_auxiliaires) + coût_ECS (si applicable)",
            ],
        },
        {
            "heading": "Exemple rapide",
            "lines": [
                "Surface=120 m², insulation=bon (50 W/m²), climate=tempéré (×1.0)",
                "Puissance = (120 × 50 × 1.0 × 1.10) / 1000 = 6.6 kW",
                "Si air_eau (1400 €/kW) : base = 6.6 × 1400 = 9240 €",
                "Ex: coûts auxiliaires = sum(...) ; ECS air_eau = 2500 € → Total = base ajusté + aux + 2500",
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
        for line in sec["lines"]:
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
