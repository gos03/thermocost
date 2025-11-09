from pydantic import BaseModel, Field
from typing import Literal

# -----------------------------
# Définition des types possibles
# -----------------------------
InsulationLevel = Literal["très_bon", "bon", "moyen", "mauvais"]
ClimateZone = Literal["doux", "tempéré", "froid"]
HeatPumpType = Literal["air_air", "air_eau", "geothermie"]
EmittersType = Literal["radiateurs_basse_t", "radiateurs_haut_t", "plancher_chauffant"]

# -----------------------------
# Paramètres de calcul
# -----------------------------

# Déperditions thermiques (W/m²)
INSULATION_W_PER_M2 = {
    "très_bon": 30,
    "bon": 50,
    "moyen": 80,
    "mauvais": 120,
}

# Facteur climatique
CLIMATE_MULTIPLIER = {
    "doux": 0.9,
    "tempéré": 1.0,
    "froid": 1.2,
}

# Coût de base (€/kW installé)
BASE_COST_PER_KW = {
    "air_air": 900,      # matériel + pose (hors aides)
    "air_eau": 1400,
    "geothermie": 2200,
}

# Facteurs selon type d’émetteurs
EMITTERS_FACTOR = {
    "radiateurs_basse_t": 1.0,
    "radiateurs_haut_t": 1.15,
    "plancher_chauffant": 1.1,
}

# Facteurs selon complexité du chantier
COMPLEXITY_FACTOR = {
    "simple": 1.0,
    "standard": 1.1,
    "complexe": 1.25,
}

# Surcoût selon gamme de marque
BRAND_PREMIUM = {
    "entrée_de_gamme": 0.95,
    "milieu_de_gamme": 1.0,
    "premium": 1.15,
}

# Coût de l’ECS (Eau Chaude Sanitaire)
DHW_COST_BY_TYPE = {
    "air_air": 0,         # pas d’ECS native
    "air_eau": 2500,
    "geothermie": 3000,
}

# Coûts auxiliaires fixes
AUX_FLAT_COSTS = {
    "electrique": 800,    # ligne dédiée, protections
    "hydraulique": 600,   # vannes, disconnecteur, pot à boues…
    "mise_en_service": 450,
}

# -----------------------------
# Modèles de données
# -----------------------------
class InputParams(BaseModel):
    """Paramètres d’entrée pour l’estimation."""
    surface_m2: float = Field(gt=10, description="Surface chauffée en m²")
    insulation: InsulationLevel
    climate: ClimateZone
    hp_type: HeatPumpType
    emitters: EmittersType
    complexity: Literal["simple", "standard", "complexe"] = "standard"
    needs_dhw: bool = True
    brand: Literal["entrée_de_gamme", "milieu_de_gamme", "premium"] = "milieu_de_gamme"


class Estimate(BaseModel):
    """Résultat complet du calcul."""
    required_kw: float
    base_cost_eur: float
    aux_costs_eur: float
    dhw_cost_eur: float
    total: float
    details: dict

# -----------------------------
# Classe de calcul
# -----------------------------
class CostModel:
    """Effectue le calcul de dimensionnement et de coût."""

    @staticmethod
    def size_required_kw(surface_m2: float, insulation: InsulationLevel, climate: ClimateZone) -> float:
        """Calcule la puissance nécessaire (kW) selon isolation et climat."""
        specific_w = INSULATION_W_PER_M2[insulation]
        clim_mult = CLIMATE_MULTIPLIER[climate]
        required_w = surface_m2 * specific_w * clim_mult
        # +10% de marge pour pics de déperdition
        required_w *= 1.10
        return round(required_w / 1000, 2)

    @staticmethod
    def estimate(params: InputParams) -> Estimate:
        """Renvoie l’estimation complète à partir des paramètres."""
        required_kw = CostModel.size_required_kw(
            params.surface_m2, params.insulation, params.climate
        )

        cost_per_kw = BASE_COST_PER_KW[params.hp_type]

        # coût de base ajusté par différents facteurs
        base = required_kw * cost_per_kw
        base *= EMITTERS_FACTOR[params.emitters]
        base *= COMPLEXITY_FACTOR[params.complexity]
        base *= BRAND_PREMIUM[params.brand]

        # coûts auxiliaires et ECS
        aux = sum(AUX_FLAT_COSTS.values())
        dhw = DHW_COST_BY_TYPE[params.hp_type] if params.needs_dhw else 0

        total = max(0, base + aux + dhw)

        return Estimate(
            required_kw=required_kw,
            base_cost_eur=round(base, 0),
            aux_costs_eur=round(aux, 0),
            dhw_cost_eur=round(dhw, 0),
            total=round(total, 0),
            details={
                "cost_per_kw": cost_per_kw,
                "emitters_factor": EMITTERS_FACTOR[params.emitters],
                "complexity_factor": COMPLEXITY_FACTOR[params.complexity],
                "brand_premium": BRAND_PREMIUM[params.brand],
            },
        )
