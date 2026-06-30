import json
import folium
import streamlit as st
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

# ==============================================================================
# 1. CHARGEMENT DONNÉES (SANS GEOPANDAS POUR ÉVITER SHAPELY/PROJ/FIONA)
# ==============================================================================

with open("departements.geojson", "r", encoding="utf-8") as f:
    gdf_dept = json.load(f)

with open("epci-100m.geojson", "r", encoding="utf-8") as f:
    gdf_epci = json.load(f)

# ==============================================================================
# 2. STREAMLIT
# ==============================================================================

st.set_page_config(layout="wide")
st.title("Exposition au ruissellement")

m = folium.Map(
    location=[46.6, 2.5],
    zoom_start=6,
    tiles="OpenStreetMap",
    prefer_canvas=True
)

Fullscreen().add_to(m)

# ==============================================================================
# 3. TA FONCTION COULEURS (STRICTEMENT IDENTIQUE)
# ==============================================================================

def determiner_style_dept(feature):
    props = feature["properties"]

    nom_actuel = str(props.get("nom", ""))
    code_actuel = str(props.get("code", ""))

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
        "Vendée" in nom_actuel or code_actuel == "85" or
        "Pas-de-Calais" in nom_actuel or code_actuel == "62" or
        "Charente-Maritime" in nom_actuel or code_actuel == "17" or
        "Alpes-Maritimes" in nom_actuel or code_actuel == "06" or
        "Savoie" in nom_actuel or code_actuel == "73" or
        "Aisne" in nom_actuel or code_actuel == "02" or
        "Loiret" in nom_actuel or code_actuel == "45" or
        "Oise" in nom_actuel or code_actuel == "60" or
        "Deux-Sèvres" in nom_actuel or code_actuel == "79" or
        "Charente" in nom_actuel or code_actuel == "16" or
        "Lot" in nom_actuel or code_actuel == "46" or
        "Aube" in nom_actuel or code_actuel == "10" or
        "Indre" in nom_actuel or code_actuel == "36" or
        "Hautes-Alpes" in nom_actuel or code_actuel == "05" or
        "Lozère" in nom_actuel or code_actuel == "48" or
        "Ardèche" in nom_actuel or code_actuel == "07" or
        "Cher" in nom_actuel or code_actuel == "18" or
        "Haute-Loire" in nom_actuel or code_actuel == "43"
    ):
        couleur = "#FF69B4"

    elif (
        "Gers" in nom_actuel or code_actuel == "32" or
        "Pyrénées-Atlantiques" in nom_actuel or code_actuel == "64" or
        "Dordogne" in nom_actuel or code_actuel == "24" or
        "Finistère" in nom_actuel or code_actuel == "29" or
        "Côtes-d'Armor" in nom_actuel or code_actuel == "22" or
        "Morbihan" in nom_actuel or code_actuel == "56" or
        "Ille-et-Vilaine" in nom_actuel or code_actuel == "35" or
        "Lot-et-Garonne" in nom_actuel or code_actuel == "47" or
        "Calvados" in nom_actuel or code_actuel == "14" or
        "Orne" in nom_actuel or code_actuel == "61" or
        "Haute-Vienne" in nom_actuel or code_actuel == "87" or
        "Creuse" in nom_actuel or code_actuel == "23" or
        "Corrèze" in nom_actuel or code_actuel == "19" or
        "Manche" in nom_actuel or code_actuel == "50" or
        "Marne" in nom_actuel or code_actuel == "51" or
        "Ariège" in nom_actuel or code_actuel == "09" or
        "Haute-Garonne" in nom_actuel or code_actuel == "31" or
        "Yonne" in nom_actuel or code_actuel == "89" or
        "Loir-et-Cher" in nom_actuel or code_actuel == "41" or
        "Tarn" in nom_actuel or code_actuel == "81" or
        "Aveyron" in nom_actuel or code_actuel == "12" or
        "Cantal" in nom_actuel or code_actuel == "15" or
        "Mayenne" in nom_actuel or code_actuel == "53" or
        "Sarthe" in nom_actuel or code_actuel == "72" or
        "Maine-et-Loire" in nom_actuel or code_actuel == "49" or
        "Haute-Saône" in nom_actuel or code_actuel == "70" or
        "Haut-Rhin" in nom_actuel or code_actuel == "68" or
        "Allier" in nom_actuel or code_actuel == "03" or
        "Nièvre" in nom_actuel or code_actuel == "58" or
        "Vienne" in nom_actuel or code_actuel == "86" or
        "Indre-et-Loire" in nom_actuel or code_actuel == "37" or
        "Alpes-de-Haute-Provence" in nom_actuel or code_actuel == "04" or
        "Saône-et-Loire" in nom_actuel or code_actuel == "71" or
        "Rhône" in nom_actuel or code_actuel == "69" or
        "Loire" in nom_actuel or code_actuel == "42"
    ):
        couleur = "#FFB6C1"

    elif (
        "Bas-Rhin" in nom_actuel or code_actuel == "67" or
        "Moselle" in nom_actuel or code_actuel == "57" or
        "Ardennes" in nom_actuel or code_actuel == "08" or
        "Vosges" in nom_actuel or code_actuel == "88" or
        "Meuse" in nom_actuel or code_actuel == "55"
    ):
        couleur = "#FFF5EE"

    else:
        couleur = "#f8f9fa"

    return {
        "fillColor": couleur,
        "fillOpacity": 0.85,
        "weight": 0,
        "color": "none"
    }

# ==============================================================================
# 4. COUCHES
# ==============================================================================

folium.GeoJson(
    gdf_dept,
    name="Départements",
    style_function=determiner_style_dept
).add_to(m)

folium.GeoJson(
    gdf_epci,
    name="EPCI",
    style_function=lambda x: {"fillOpacity": 0, "color": "#FFFFFF", "weight": 1},
    highlight_function=lambda x: {"color": "#FF0000", "weight": 2.5},

    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "siren"],
        aliases=["Intercommunalité :", "SIREN :"],
        sticky=True
    ),

    popup=folium.GeoJsonPopup(
        fields=["nom", "siren"],
        aliases=["Nom EPCI :", "Numéro SIREN :"]
    )
).add_to(m)

# ==============================================================================
# 5. RENDU
# ==============================================================================

st_folium(m, width=1100, height=800)
