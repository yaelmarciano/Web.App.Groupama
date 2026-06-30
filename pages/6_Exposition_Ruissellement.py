import os
import folium
import geopandas as gpd
import streamlit as st
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

# ==============================================================================
# 1. CHARGEMENT DONNÉES
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

# Colonnes
colonne_trouvee = "nom"
for c in ["nom", "NOM", "nom_dept", "NOM_DEPT", "Nom"]:
    if c in gdf_dept.columns:
        colonne_trouvee = c
        break

col_nom_epci = "nom" if "nom" in gdf_epci.columns else "NOM"
col_code_epci = "siren" if "siren" in gdf_epci.columns else "code"

# ==============================================================================
# 2. STREAMLIT
# ==============================================================================

st.set_page_config(layout="wide")
st.title("Exposition au risque de ruissellement")

m = folium.Map(
    location=[46.6, 2.5],
    zoom_start=6,
    tiles="OpenStreetMap",
    prefer_canvas=True
)

Fullscreen().add_to(m)

# ==============================================================================
# 3. TES COULEURS (INCHANGÉES)
# ==============================================================================

def style_dept(feature):
    nom = str(feature["properties"].get(colonne_trouvee, ""))
    code = str(feature["properties"].get("code", ""))

    if (
        "Landes" in nom or code == "40" or
        "Var" in nom or code == "83" or
        "Gard" in nom or code == "30" or
        "Hérault" in nom or code == "34" or
        "Gironde" in nom or code == "33" or
        "Paris" in nom or code == "75"
    ):
        couleur = "#4B0082"

    elif (
        "Seine-Maritime" in nom or code == "76"
    ):
        couleur = "#FF1493"

    elif (
        "Loire-Atlantique" in nom or code == "44"
    ):
        couleur = "#FF69B4"

    elif (
        "Gers" in nom or code == "32"
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
    style_function=style_dept
).add_to(m)

# ==============================================================================
# 4. EPCI (CLICK = NOM + SIREN)
# ==============================================================================

def style_epci(feature):
    return {
        "fillOpacity": 0,
        "color": "#FFFFFF",
        "weight": 1
    }

def highlight_epci(feature):
    return {
        "color": "#FF0000",
        "weight": 2
    }

def popup_epci(feature):
    props = feature["properties"]
    nom = props.get(col_nom_epci, "N/A")
    code = props.get(col_code_epci, "N/A")

    return folium.Popup(
        f"<b>{nom}</b><br>SIREN : {code}",
        max_width=300
    )

folium.GeoJson(
    gdf_epci,
    style_function=style_epci,
    highlight_function=highlight_epci,
    popup=popup_epci
).add_to(m)

# ==============================================================================
# 5. LÉGENDE
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
width:320px;
">
<b>Exposition au ruissellement</b><br><br>

<div>■ violet : zones fortes</div>
<div>■ rose : zones moyennes</div>
<div>■ beige : zones faibles</div>

</div>
"""

m.get_root().html.add_child(folium.Element(html_legende))

# ==============================================================================
# 6. AFFICHAGE STREAMLIT
# ==============================================================================

st_folium(m, width=1000, height=800)
