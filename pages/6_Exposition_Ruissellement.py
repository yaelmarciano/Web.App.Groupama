import os
import folium
import geopandas as gpd
import streamlit as st
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

# ==============================================================================
# 1. PAGE STREAMLIT
# ==============================================================================
st.set_page_config(layout="wide")
st.title("Exposition au risque de ruissellement")

# ==============================================================================
# 2. CHARGEMENT DONNÉES
# ==============================================================================

chemin_dept = "departements.geojson"
chemin_epci = "epci-100m.geojson"

gdf_dept = gpd.read_file(chemin_dept)
gdf_epci = gpd.read_file(chemin_epci)

if gdf_dept.crs is not None:
    gdf_dept = gdf_dept.to_crs(epsg=4326)

if gdf_epci.crs is not None:
    gdf_epci = gdf_epci.to_crs(epsg=4326)

gdf_epci["geometry"] = gdf_epci["geometry"].simplify(
    tolerance=0.008,
    preserve_topology=True
)

# Détection colonnes départements
colonne_trouvee = "nom"
for col in ["nom", "NOM", "nom_dept", "NOM_DEPT", "Nom"]:
    if col in gdf_dept.columns:
        colonne_trouvee = col
        break

# EPCI colonnes
colonne_code_epci = "siren" if "siren" in gdf_epci.columns else "code"
colonne_nom_epci = "nom" if "nom" in gdf_epci.columns else "NOM"

# ==============================================================================
# 3. CARTE
# ==============================================================================

m = folium.Map(
    location=[46.6, 2.5],
    zoom_start=6,
    tiles="OpenStreetMap",
    prefer_canvas=True
)

Fullscreen().add_to(m)

# ==============================================================================
# 4. STYLE DÉPARTEMENTS (TES COULEURS CONSERVÉES)
# ==============================================================================

def style_dept(feature):
    nom = str(feature["properties"].get(colonne_trouvee, ""))
    code = str(feature["properties"].get("code", ""))

    # VIOLET
    if (
        "Landes" in nom or code == "40" or
        "Var" in nom or code == "83" or
        "Gard" in nom or code == "30" or
        "Hérault" in nom or code == "34" or
        "Gironde" in nom or code == "33" or
        "Nord" in nom or code == "59" or
        "Paris" in nom or code == "75"
    ):
        couleur = "#4B0082"

    # ROSE FUCHSIA
    elif (
        "Seine-Maritime" in nom or code == "76" or
        "Eure" in nom or code == "27"
    ):
        couleur = "#FF1493"

    # ROSE
    elif (
        "Hautes-Pyrénées" in nom or code == "65" or
        "Loire-Atlantique" in nom or code == "44"
    ):
        couleur = "#FF69B4"

    # BEIGE
    elif (
        "Gers" in nom or code == "32" or
        "Finistère" in nom or code == "29"
    ):
        couleur = "#FFB6C1"

    else:
        couleur = "#f8f9fa"

    return {
        "fillColor": couleur,
        "fillOpacity": 0.85,
        "weight": 0,
        "color": "none"
    }

folium.GeoJson(
    gdf_dept,
    style_function=style_dept,
    name="Départements"
).add_to(m)

# ==============================================================================
# 5. EPCI (CORRIGÉ POUR STREAMLIT = PAS DE CRASH)
# ==============================================================================

def style_epci(feature):
    return {
        "fillOpacity": 0,
        "color": "#111111",
        "weight": 0.6
    }

def highlight_epci(feature):
    return {
        "color": "#FF0000",
        "weight": 2
    }

folium.GeoJson(
    gdf_epci,
    style_function=style_epci,
    highlight_function=highlight_epci
).add_to(m)

# ==============================================================================
# 6. LÉGENDE HTML (TON STYLE CONSERVÉ)
# ==============================================================================

html_legende = """
<div style="
position: fixed;
top: 20px;
right: 20px;
z-index:9999;
background:white;
padding:15px;
border-radius:8px;
box-shadow:0 0 15px rgba(0,0,0,0.2);
font-size:13px;
width:300px;
">
<b>Exposition au ruissellement</b><br><br>

<div>■ violet : >15%</div>
<div>■ rose foncé : 12-15%</div>
<div>■ rose : 9-12%</div>
<div>■ beige : 6-9%</div>
<div>■ fond : 0%</div>

</div>
"""

m.get_root().html.add_child(folium.Element(html_legende))

# ==============================================================================
# 7. AFFICHAGE STREAMLIT
# ==============================================================================

st_folium(m, width=1000, height=800)
