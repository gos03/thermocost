import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, validator

# Charger la config JSON (nouveau format)
_CONFIG_PATH = Path(__file__).with_suffix('.json')
try:
    with _CONFIG_PATH.open('r', encoding='utf-8') as _f:
        _CFG = json.load(_f)
except Exception:
    raise RuntimeError('Impossible de charger le fichier cost_model.json')

# Exposer pièces utiles
FORM_FIELDS = _CFG.get('fields', [])
PRICING = _CFG.get('pricing_model', {})
VERSION = _CFG.get('version')
CURRENCY = _CFG.get('currency', 'EUR')
OUTPUT = _CFG.get('output', 'TTC')

# -----------------------------
# Modèles de données (nouveaux champs)
# -----------------------------
class InputParams(BaseModel):
    type_usage: str
    type_logement: str
    acces_chantier: str
    surface: float = Field(..., ge=0)
    isolation: str
    emetteurs: str
    climat: str
    temperature_max_ete_dernier: int = 25
    pieces_airair: Optional[int] = 0
    ecs_inclus: bool = False
    nb_personnes: int = Field(..., ge=1)

    @validator('pieces_airair', pre=True, always=True)
    def coerce_pieces(cls, v):
        if v is None or v == '':
            return 0
        return int(v)

    @validator('surface', pre=True)
    def coerce_surface(cls, v):
        if v is None:
            raise ValueError('surface is required')
        return float(v)

    @validator('nb_personnes', pre=True)
    def coerce_nb_personnes(cls, v):
        if v is None:
            raise ValueError('nb_personnes is required')
        return int(v)


class Estimate(BaseModel):
    cout_ht: float
    cout_ttc: float
    tva: float
    details: dict


# -----------------------------
# Classe de calcul selon pricing_model.formula
# -----------------------------
class CostModel:
    @staticmethod
    def estimate(params: InputParams) -> Estimate:
        pricing = PRICING

        # base_m2_ht
        base_m2_ht_map = pricing.get('base_m2_ht', {})
        base_m2_ht = base_m2_ht_map.get(params.type_usage)
        if base_m2_ht is None:
            raise ValueError(f'Unknown type_usage: {params.type_usage}')

        # coefficients
        coef_iso = pricing.get('coef_isolation', {}).get(params.isolation, 1.0)
        coef_clim = pricing.get('coef_climat', {}).get(params.climat, 1.0)

        # surface corrigée
        surface_corr = params.surface * coef_iso * coef_clim
        base_ht = surface_corr * base_m2_ht

        coef_log = pricing.get('coef_logement', {}).get(params.type_logement, 1.0)
        coef_acces = pricing.get('coef_acces_chantier', {}).get(params.acces_chantier, 1.0)
        coef_emit = pricing.get('coef_emetteurs', {}).get(params.emetteurs, 1.0)

        # air-air pieces handling
        coef_airair = 1.0
        if 'Air-air' in params.type_usage:
            airair = pricing.get('airair_pieces', {})
            base_incl = airair.get('base_pieces_incluses', 3)
            incr = airair.get('increment_coef_par_piece_sup', 0.05)
            extra = max(0, (params.pieces_airair or 0) - base_incl)
            coef_airair = max(airair.get('coef_min', 1.0), 1.0 + extra * incr)

        # ECS cost
        ecs_conf = pricing.get('ecs', {})
        cout_ecs_ht = 0
        if params.ecs_inclus:
            cout_ecs_ht = ecs_conf.get('cout_ecs_ht_base', 0) + ecs_conf.get('cout_ecs_ht_par_personne', 0) * params.nb_personnes

        coef_global = coef_log * coef_acces * coef_emit * coef_airair
        cout_ht = base_ht * coef_global + cout_ecs_ht

        # Déterminer la TVA : utiliser systématiquement la TVA standard (20%)
        tva_conf = pricing.get('tva', {})
        tva = tva_conf.get('standard', 0.2)

        cout_ttc = cout_ht * (1 + tva)

        details = {
            'base_m2_ht': base_m2_ht,
            'coef_iso': coef_iso,
            'coef_clim': coef_clim,
            'surface_corr': round(surface_corr, 2),
            'base_ht': round(base_ht, 2),
            'coef_log': coef_log,
            'coef_acces': coef_acces,
            'coef_emit': coef_emit,
            'coef_airair': round(coef_airair, 3),
            'cout_ecs_ht': round(cout_ecs_ht, 2),
            'coef_global': round(coef_global, 3),
        }

        return Estimate(cout_ht=round(cout_ht, 2), cout_ttc=round(cout_ttc, 2), tva=round(tva, 3), details=details)


# utilitaire pour templates
def get_form_spec():
    return FORM_FIELDS
