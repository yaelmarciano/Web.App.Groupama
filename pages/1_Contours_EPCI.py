
import streamlit as st
import geopandas as gpd
import folium
from folium.plugins import Fullscreen

st.set_page_config(layout="wide")

st.title("Carte interactive des EPCI")

# 🔍 BARRE DE RECHERCHE (AJOUTÉE)
recherche = st.text_input("🔍 Rechercher un EPCI (nom ou code SIREN)")

# =========================
# 1. CHARGEMENT
# =========================
path = "epci-100m.geojson"

@st.cache_data
def load_geo_data(file_path):
    gdf_raw = gpd.read_file(file_path)

    if gdf_raw.crs is None:
        gdf_raw.set_crs("EPSG:4326", inplace=True)
    elif gdf_raw.crs != "EPSG:4326":
        gdf_raw = gdf_raw.to_crs("EPSG:4326")

    return gdf_raw

gdf = load_geo_data(path)

# =========================
# 🔍 FILTRAGE SI RECHERCHE
# =========================
gdf_affiche = gdf.copy()

if recherche:
    gdf_affiche = gdf[
        gdf["nom"].str.contains(recherche, case=False, na=False)
        | gdf["code"].astype(str).str.contains(recherche, na=False)
    ]

# =========================
# CARTE
# =========================
xmin, ymin, xmax, ymax = gdf_affiche.total_bounds

m = folium.Map(tiles=None)
m.fit_bounds([[ymin, xmin], [ymax, xmax]])

Fullscreen().add_to(m)

def style_function(feature):
    return {"fillOpacity": 0, "color": "black", "weight": 0.8}

def highlight_function(feature):
    return {"color": "red", "weight": 3}

folium.GeoJson(
    gdf_affiche,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(fields=["nom", "code"])
).add_to(m)

# =========================
# AFFICHAGE CORRIGÉ
# =========================
st.components.v1.html(m._repr_html_(), height=700)
