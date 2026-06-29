# ==============================================================================
# 1. IMPORTS
# ==============================================================================
import json
import branca.colormap as cm
import folium
import geopandas as gpd
from folium.plugins import Fullscreen
from IPython.display import HTML, display
from shapely.geometry import shape

# ==============================================================================
# 2. CHARGEMENT DES DEUX DONNÉES (DÉPARTEMENTS & EPCI)
# ==============================================================================
print("1/4 - Lecture du GeoJSON des départements...")
# Lit le fichier directement dans ton dossier GitHub
with open("departements.geojson", "r", encoding="utf-8") as f:
    departements_geojson = json.load(f)

print("2/4 - Lecture et SIMPLIFICATION du GeoJSON des EPCI...")
# Lit le fichier directement dans ton dossier GitHub
with open("epci-100m.geojson", "r", encoding="utf-8") as f:
    epci_data = json.load(f)

rows = []
for feat in epci_data["features"]:
    rows.append(
        {
            "siren": feat["properties"]["code"],
            "nom": feat["properties"]["nom"],
            "geometry": shape(feat["geometry"]),
        }
    )

gdf_epci = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")

# Simplification pour que la carte s'affiche rapidement
gdf_epci["geometry"] = gdf_epci["geometry"].simplify(
    tolerance=0.005, preserve_topology=True
)

xmin, ymin, xmax, ymax = gdf_epci.total_bounds

# ==============================================================================
# 3. DONNÉES DE COULEURS (PR%) PAR DÉPARTEMENT
# ==============================================================================
departement_values = {
    "59": 104,
    "62": 104,
    "02": 104,
    "08": 104,
    "57": 104,
    "67": 104,
    "68": 104,
    "54": 104,
    "55": 104,
    "88": 104,
    "52": 104,
    "10": 104,
    "51": 104,
    "60": 100,
    "80": 100,
    "76": 104,
    "27": 104,
    "78": 100,
    "95": 100,
    "77": 100,
    "93": 100,
    "94": 100,
    "75": 100,
    "92": 103,
    "91": 104,
    "29": 100,
    "22": 100,
    "35": 100,
    "56": 100,
    "14": 100,
    "50": 100,
    "61": 100,
    "28": 104,
    "45": 100,
    "41": 100,
    "37": 100,
    "36": 100,
    "18": 100,
    "23": 100,
    "03": 100,
    "58": 100,
    "71": 100,
    "21": 104,
    "89": 104,
    "70": 104,
    "25": 104,
    "39": 104,
    "90": 104,
    "44": 100,
    "49": 100,
    "72": 100,
    "53": 100,
    "85": 100,
    "79": 100,
    "86": 100,
    "87": 100,
    "16": 104,
    "17": 104,
    "33": 100,
    "24": 104,
    "19": 100,
    "15": 100,
    "43": 100,
    "63": 100,
    "47": 100,
    "40": 100,
    "64": 100,
    "32": 100,
    "82": 100,
    "46": 104,
    "31": 100,
    "09": 85,
    "65": 88,
    "11": 100,
    "66": 100,
    "12": 100,
    "81": 100,
    "34": 104,
    "30": 104,
    "48": 104,
    "13": 100,
    "83": 100,
    "06": 100,
    "84": 100,
    "04": 100,
    "05": 100,
    "26": 100,
    "07": 104,
    "69": 104,
    "42": 100,
    "38": 100,
    "73": 100,
    "74": 105,
    "01": 104,
    "2A": 100,
    "2B": 100,
}

colors_scale = [
    "#6b3a1f",
    "#a0672a",
    "#c8a96e",
    "#e8d9b5",
    "#f5f0e8",
    "#c8e8d8",
    "#8dd0c0",
    "#4db8a8",
    "#00897b",
]
index_vals = [65, 75, 85, 95, 100, 105, 115, 125, 135]

colormap = cm.LinearColormap(
    colors=colors_scale, vmin=65, vmax=135, index=index_vals, caption="PR [%]"
)

# ==============================================================================
# 4. INITIALISATION DE LA CARTE
# ==============================================================================
print("3/4 - Initialisation de la carte...")
m = folium.Map(
    location=[46.5, 2.5],
    zoom_start=6,
    tiles="CartoDB positron",
    control_scale=True,
    prefer_canvas=True,
)

m.fit_bounds([[ymin, xmin], [ymax, xmax]])

Fullscreen(
    position="topright",
    title="Plein écran",
    title_cancel="Quitter",
    force_separate_button=True,
).add_to(m)

# ==============================================================================
# 5. SUPERPOSITION DES COUCHES (DÉPARTEMENTS EN BAS, EPCI EN HAUT)
# ==============================================================================


# --- A. Fond de couleur Départemental ---
def style_departement(feature):
    dep_code = feature["properties"].get("code", "")
    value = departement_values.get(dep_code, 100)
    return {
        "fillColor": colormap(value),
        "fillOpacity": 0.85,
        "color": "none",
        "weight": 0,
    }


folium.GeoJson(
    departements_geojson,
    name="Couleurs Précipitations (Dép)",
    style_function=style_departement,
    interactive=False,
).add_to(m)


# --- B. Contours Fins des EPCI ---
def style_epci(feature):
    return {"fillOpacity": 0, "color": "#111111", "weight": 0.5}


def highlight_epci(feature):
    return {"fillOpacity": 0.1, "color": "#FF0000", "weight": 2.0}


tooltip_epci = folium.GeoJsonTooltip(
    fields=["nom", "siren"], aliases=["Intercommunalité :", "Code SIREN :"], sticky=True
)

folium.GeoJson(
    gdf_epci,
    name="Contours EPCI",
    style_function=style_epci,
    highlight_function=highlight_epci,
    tooltip=tooltip_epci,
).add_to(m)

# ==============================================================================
# 6. HABILLAGE ET RENDU COMPLET
# ==============================================================================
colormap.add_to(m)

title_html = """
<div style="position: fixed; top: 10px; left: 60px; z-index: 9999; background: white; padding: 10px 14px; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.25); font-family: Arial, sans-serif; max-width: 380px;">
    <div style="font-size:12px; font-weight:bold; color:#222;">
        Cumul annuel de précipitations : rapport (%) à référence 1976-2005<br>pour l'horizon lointain (2071-2100)
    </div>
    <div style="font-size:11px; color:#555; margin-top:4px;">
        Scénario d'émissions modérées (RCP4.5) — Découpage EPCI
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))
folium.LayerControl().add_to(m)

print("4/4 - Affichage graphique de la carte...")
display(HTML(m._repr_html_()))
