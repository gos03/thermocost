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
            "heading": "1) Données d'entrée",
            "lines": lambda: [f"- {f['id']}: {f.get('label', f['id'])}" for f in get_form_spec()],
        },
        {
            "heading": "2) Paramètres de base — base_m2_ht (€/m² HT)",
            "lines": lambda: format_dict(PRICING.get('base_m2_ht', {})),
        },
        {
            "heading": "3) Coefficients d'isolation",
            "lines": lambda: format_dict(PRICING.get('coef_isolation', {})),
        },
        {
            "heading": "4) Coefficients climatiques",
            "lines": lambda: format_dict(PRICING.get('coef_climat', {})),
        },
        {
            "heading": "5) Coefficients type logement",
            "lines": lambda: format_dict(PRICING.get('coef_logement', {})),
        },
        {
            "heading": "6) Coefficients accès chantier",
            "lines": lambda: format_dict(PRICING.get('coef_acces_chantier', {})),
        },
        {
            "heading": "7) Coefficients émetteurs",
            "lines": lambda: format_dict(PRICING.get('coef_emetteurs', {})),
        },
        {
            "heading": "8) Gestion air-air (pièces supplémentaires)",
            "lines": lambda: format_dict(PRICING.get('airair_pieces', {})),
        },
        {
            "heading": "9) Coûts ECS (Eau Chaude Sanitaire)",
            "lines": lambda: format_dict({k: v for k, v in PRICING.get('ecs', {}).items() if k != 'enabled_if'}),
        },
        {
            "heading": "10) Taux de TVA",
            "lines": lambda: format_dict(PRICING.get('tva', {})),
        },
        {
            "heading": "11) Formule de calcul",
            "lines": [
                "étape 1: surface_corr = surface × coef_isolation × coef_climat",
                "étape 2: base_ht = surface_corr × base_m2_ht[type_usage]",
                "étape 3: coef_global = coef_logement × coef_acces_chantier × coef_emetteurs × coef_airair",
                "étape 4: cout_ecs_ht = (ecs_inclus ? cout_ecs_ht_base + cout_ecs_ht_par_personne × nb_personnes : 0)",
                "étape 5: cout_ht = base_ht × coef_global + cout_ecs_ht",
                "étape 6: cout_ttc = cout_ht × (1 + tva_standard = 0.20)",
            ],
        },
        {
            "heading": "12) Exemple de calcul",
            "lines": [
                "Scenario: Air-eau (chauffage + ECS), Maison individuelle, 120 m²",
                "  - type_usage: Air-eau (chauffage + ECS) → base_m2_ht = 110 €/m²",
                "  - isolation: Moyenne → coef_iso = 1.0",
                "  - climat: Zone tempérée → coef_clim = 1.0",
                "  - surface_corr = 120 × 1.0 × 1.0 = 120 m²",
                "  - base_ht = 120 × 110 = 13 200 €",
                "  - coef_global = 1.0 (logement) × 1.0 (acces) × 1.0 (emetteurs) × 1.0 (airair) = 1.0",
                "  - cout_ecs_ht = 800 + 250 × 3 = 1 550 € (pour 3 personnes)",
                "  - cout_ht = 13 200 × 1.0 + 1 550 = 14 750 €",
                "  - cout_ttc = 14 750 × 1.20 = 17 700 €",
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
