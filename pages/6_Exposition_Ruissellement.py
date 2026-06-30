import streamlit as st
import folium
from folium.plugins import Fullscreen
import geopandas as gpd
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Exposition au risque de ruissellement")

# ==============================================================================
# 1. CHARGEMENT DES DONNÉES (GitHub raw)
# ==============================================================================

chemin_dept = "https://raw.githubusercontent.com/VOTRE_COMPTE/VOTRE_REPO/main/departements.geojson"
chemin_epci = "https://raw.githubusercontent.com/VOTRE_COMPTE/VOTRE_REPO/main/epci-100m.geojson"

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
for col in ['nom', 'NOM', 'nom_dept', 'NOM_DEPT', 'Nom']:
    if col in gdf_dept.columns:
        colonne_trouvee = col
        break

# Détection colonnes EPCI
colonne_code_epci = "siren" if "siren" in gdf_epci.columns else ("code" if "code" in gdf_epci.columns else "CODE")
colonne_nom_epci = "nom" if "nom" in gdf_epci.columns else ("NOM" if "NOM" in gdf_epci.columns else "NOM_EPCI")

# ==============================================================================
# 2. CARTE FOLIUM
# ==============================================================================

m = folium.Map(
    location=[46.6, 2.5],
    zoom_start=6,
    tiles="OpenStreetMap",
    prefer_canvas=True
)

Fullscreen(
    position="topleft",
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True
).add_to(m)

# ==============================================================================
# 3. STYLE DÉPARTEMENTS
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
        "Paris" in nom_actuel or code_actuel == "75"
    ):
        couleur = "#4B0082"

    elif (
        "Seine-Maritime" in nom_actuel or code_actuel == "76" or
        "Eure" in nom_actuel or code_actuel == "27"
    ):
        couleur = "#FF1493"

    elif (
        "Hautes-Pyrénées" in nom_actuel or code_actuel == "65" or
        "Loire-Atlantique" in nom_actuel or code_actuel == "44"
    ):
        couleur = "#FF69B4"

    elif (
        "Gers" in nom_actuel or code_actuel == "32" or
        "Finistère" in nom_actuel or code_actuel == "29"
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
    style_function=determiner_style_dept,
    name="Départements"
).add_to(m)

# ==============================================================================
# 4. EPCI
# ==============================================================================

def style_base_epci(feature):
    return {
        "fillColor": "rgba(0,0,0,0)",
        "fillOpacity": 0,
        "color": "#FFFFFF",
        "weight": 1.0
    }

def style_highlight_epci(feature):
    return {
        "color": "#FF0000",
        "weight": 2.5
    }

folium.GeoJson(
    gdf_epci,
    name="EPCI",
    style_function=style_base_epci,
    highlight_function=style_highlight_epci,
    tooltip=folium.GeoJsonTooltip(
        fields=[colonne_nom_epci, colonne_code_epci],
        aliases=["Intercommunalité :", "Code SIREN :"]
    ),
    popup=folium.GeoJsonPopup(
        fields=[colonne_nom_epci, colonne_code_epci],
        aliases=["Nom EPCI :", "SIREN :"]
    )
).add_to(m)

# ==============================================================================
# 5. LÉGENDE HTML
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
<b>Exposition au Ruissellement</b><br><br>

<div><span style="color:#4B0082;">■</span> > 15%</div>
<div><span style="color:#FF1493;">■</span> 12-15%</div>
<div><span style="color:#FF69B4;">■</span> 9-12%</div>
<div><span style="color:#FFB6C1;">■</span> 6-9%</div>
<div><span style="color:#f8f9fa;">■</span> 0%</div>

</div>
"""

m.get_root().html.add_child(folium.Element(html_legende))

# ==============================================================================
# 6. AFFICHAGE STREAMLIT
# ==============================================================================

bounds = [
    [gdf_epci.total_bounds[1], gdf_epci.total_bounds[0]],
    [gdf_epci.total_bounds[3], gdf_epci.total_bounds[2]]
]

m.fit_bounds(bounds)

st_folium(m, width=None, height=800)
