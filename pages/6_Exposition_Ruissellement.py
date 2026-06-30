import os
import folium
import geopandas as gpd
import streamlit as st
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

# ==============================================================================
# 1. DONNÉES
# ==============================================================================

gdf_dept = gpd.read_file("departements.geojson")
gdf_epci = gpd.read_file("epci-100m.geojson")

if gdf_dept.crs:
    gdf_dept = gdf_dept.to_crs(4326)

if gdf_epci.crs:
    gdf_epci = gdf_epci.to_crs(4326)

gdf_epci["geometry"] = gdf_epci["geometry"].simplify(
    tolerance=0.008,
    preserve_topology=True
)

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
# 3. 🔥 TON CODE ORIGINAL (INCHANGÉ)
# ==============================================================================

def determiner_style_dept(feature):
    nom_actuel = str(feature['properties'].get(colonne_trouvee, ''))
    code_actuel = str(feature['properties'].get('code', ''))

    if (
        "Landes" in nom_actuel or code_actuel == "40" or
        "Var" in nom_actuel or code_actuel == "83" or
        "Gard" in nom_actuel or code_actuel == "30" or
        "Hérault" in nom_actuel or code_actuel == "34" or
        "Gironde" in nom_actuel or code_actuel == "33" or
        "Nord" in nom_actuel or code_actuel == "59" or
        "Hauts-de-Seine" in nom_actuel or code_actuel == "92" or
        "Val-de-Marne" in nom_actuel or code_actuel == "94" or
        "Bouches-du-Rhône" in nom_actuel or code_actuel == "13" or
        "Seine-Saint-Denis" in nom_actuel or code_actuel == "93" or
        "Paris" in nom_actuel or code_actuel == "75" or
        "Haute-Corse" in nom_actuel or code_actuel in ["2B", "2b"]
    ):
        couleur = "#4B0082"

    elif (
        "Seine-Maritime" in nom_actuel or code_actuel == "76" or
        "Eure" in nom_actuel or code_actuel == "27" or
        "Somme" in nom_actuel or code_actuel == "80" or
        "Pyrénées-Orientales" in nom_actuel or code_actuel == "66" or
        "Aude" in nom_actuel or code_actuel == "11" or
        "Doubs" in nom_actuel or code_actuel == "25" or
        "Jura" in nom_actuel or code_actuel == "39" or
        "Yvelines" in nom_actuel or code_actuel == "78" or
        "Essonne" in nom_actuel or code_actuel == "91" or
        "Vaucluse" in nom_actuel or code_actuel == "84" or
        "Puy-de-Dôme" in nom_actuel or code_actuel == "63" or
        "Côte-d'Or" in nom_actuel or code_actuel == "21" or
        "Ain" in nom_actuel or code_actuel == "01" or
        "Drôme" in nom_actuel or code_actuel == "26" or
        "Isère" in nom_actuel or code_actuel == "38" or
        "Corse-du-Sud" in nom_actuel or code_actuel in ["2A", "2a"]
    ):
        couleur = "#FF1493"

    elif (
        "Hautes-Pyrénées" in nom_actuel or code_actuel == "65" or
        "Loire-Atlantique" in nom_actuel or code_actuel == "44" or
        "Vendée" in nom_actuel or code_actuel == "85"
    ):
        couleur = "#FF69B4"

    elif (
        "Gers" in nom_actuel or code_actuel == "32" or
        "Pyrénées-Atlantiques" in nom_actuel or code_actuel == "64" or
        "Finistère" in nom_actuel or code_actuel == "29"
    ):
        couleur = "#FFB6C1"

    else:
        couleur = "#f8f9fa"

    return {
        "fillColor": couleur,
        "fillOpacity": 0.85 if couleur != "#f8f9fa" else 0.4,
        "weight": 0,
        "color": "none"
    }

folium.GeoJson(
    gdf_dept,
    name="Couleurs Départements (Fond)",
    style_function=determiner_style_dept,
    interactive=False
).add_to(m)

# ==============================================================================
# 4. EPCI (SAFE + CLICK POPUP)
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
        "weight": 2.5
    }

def popup_epci(feature):
    p = feature["properties"]
    nom = p.get(col_nom_epci, "N/A")
    code = p.get(col_code_epci, "N/A")

    return folium.Popup(f"<b>{nom}</b><br>SIREN : {code}", max_width=300)

folium.GeoJson(
    gdf_epci,
    style_function=style_epci,
    highlight_function=highlight_epci,
    popup=popup_epci
).add_to(m)

# ==============================================================================
# 5. TON CODE LÉGENDE ORIGINAL (ON NE TOUCHE PAS)
# ==============================================================================

html_legende = """
<div style="
    position: fixed; 
    top: 20px; right: 20px; width: 320px; 
    z-index:9999; font-family: Arial; font-size:13px;
    background-color: white; padding: 15px; border-radius: 8px; 
    box-shadow: 0 0 15px rgba(0,0,0,0.2);
">
    <div style="font-weight: bold; font-size: 15px;">
        Exposition au Risque de Ruissellement 
    </div>

    <div style="margin-top:10px;">
        <div><span style="color:#4B0082;">■</span> Supérieur à 15 %</div>
        <div><span style="color:#FF1493;">■</span> 12 - 15 %</div>
        <div><span style="color:#FF69B4;">■</span> 9 - 12 %</div>
        <div><span style="color:#FFB6C1;">■</span> 6 - 9 %</div>
        <div><span style="color:#f8f9fa;">■</span> 0 %</div>
    </div>

    <div style="margin-top:10px; font-size:11px;">
        Contours blancs : EPCI
    </div>
</div>
"""

m.get_root().html.add_child(folium.Element(html_legende))

# ==============================================================================
# 6. AFFICHAGE
# ==============================================================================

st_folium(m, width=1000, height=800)
