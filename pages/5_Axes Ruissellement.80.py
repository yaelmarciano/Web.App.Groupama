import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen

# 1. Configuration de la page web Streamlit
st.set_page_config(page_title="Atlas Risque Inondation", layout="wide")
st.title("Cartographie Interactive des Axes de Ruissellement par EPCI")

# Définition des fichiers locaux (présents sur ton GitHub)
CHEMIN_EPCI = "epci-100m.geojson"
CHEMIN_RUISSELLEMENT = "axes_super_legers.geojson"

# 2. Chargement des données standard (sans pyogrio)
@st.cache_data
def charger_donnees():
    # On retire 'engine="pyogrio"' pour utiliser le moteur classique par défaut
    gdf_epci = gpd.read_file(CHEMIN_EPCI)
    gdf_ruissellement = gpd.read_file(CHEMIN_RUISSELLEMENT)

    # Conversion en WGS84 pour Folium
    if gdf_ruissellement.crs is not None:
        gdf_ruissellement = gdf_ruissellement.to_crs(epsg=4326)
    if gdf_epci.crs is not None:
        gdf_epci = gdf_epci.to_crs(epsg=4326)

    return gdf_epci, gdf_ruissellement

# Indicateur de chargement visuel
with st.spinner("Chargement des cartes en cours..."):
    try:
        gdf_epci, gdf_ruissellement = charger_donnees()
        st.success("Données géographiques chargées avec succès !")
    except Exception as e:
        st.error(f"Erreur technique lors du chargement : {e}")
        st.stop()

# 3. Création de la carte Folium
m = folium.Map(tiles="OpenStreetMap")

# Bouton Plein Écran
Fullscreen(
    position="topleft",
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True
).add_to(m)

# Couche 1 : Les contours des EPCI
folium.GeoJson(
    gdf_epci,
    name="Contours des EPCI",
    style_function=lambda x: {
        "fillColor": "transparent",
        "color": "#666666",
        "weight": 1.5,
    },
    highlight_function=lambda x: {
        "fillColor": "#FF0000",
        "fillOpacity": 0.2,    
        "color": "#FF0000",    
        "weight": 3.0,         
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['nom', 'code'], 
        aliases=['Nom de l\'EPCI :', 'Numéro :'],
        localize=True
    )
).add_to(m)

# Couche 2 : Les axes de ruissellement super légers
folium.GeoJson(
    gdf_ruissellement, 
    name="Axes de ruissellement",
    style_function=lambda x: {
        "color": "#0000FF",
        "weight": 2.5
    }
).add_to(m)

# Centrage automatique
m.fit_bounds(gdf_ruissellement.total_bounds.tolist())

# Menu des couches
folium.LayerControl().add_to(m)

# 4. Affichage final dans Streamlit
st_folium(m, width=1300, height=650)
