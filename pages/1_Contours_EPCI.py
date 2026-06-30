
import streamlit as st
import geopandas as gpd
import folium
from folium.plugins import Fullscreen, Search
from streamlit_folium import st_folium

# ======================
# PAGE STREAMLIT
# ======================
st.set_page_config(layout="wide")
st.title("Carte interactive des EPCI")

# ======================
# CHARGEMENT DONNÉES
# ======================
@st.cache_data
def load_data():
    gdf = gpd.read_file("epci-100m.geojson")

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")

    # sécurise les champs
    gdf["nom"] = gdf["nom"].astype(str)
    gdf["code"] = gdf["code"].astype(str)

    return gdf

gdf = load_data()

# ======================
# CARTE
# ======================
m = folium.Map(tiles="cartodbpositron", zoom_control=True)

# zoom automatique sur la France
bounds = gdf.total_bounds
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

# bouton plein écran
Fullscreen().add_to(m)

# ======================
# COUCHE EPCI
# ======================
layer = folium.FeatureGroup(name="EPCI").add_to(m)

folium.GeoJson(
    gdf,
    name="EPCI",
    style_function=lambda x: {
        "fillOpacity": 0,
        "color": "black",
        "weight": 1
    },
    highlight_function=lambda x: {
        "color": "red",
        "weight": 3
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "code"],
        aliases=["Nom :", "SIREN :"]
    ),
).add_to(layer)

# ======================
# BARRE DE RECHERCHE
# ======================
Search(
    layer=layer,
    geom_type="Polygon",
    placeholder="Rechercher un EPCI (nom ou SIREN)",
    search_label="nom",
    search_zoom=12,
    collapsed=False
).add_to(m)
# ======================
# AFFICHAGE STREAMLIT
# ======================
st_folium(m, width=1100, height=700)
