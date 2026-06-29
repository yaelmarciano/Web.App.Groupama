import streamlit as st
import geopandas as gpd
import folium
from folium.plugins import Fullscreen

# Configuration de la page Streamlit (largeur maximale pour la carte)
st.set_page_config(layout="wide")

st.title("Carte interactive des EPCI - Risque Ruissellement")

# =========================
# 1. CHEMIN DU FICHIER (Adapté pour GitHub / Local)
# =========================
# Option A : Si le fichier 'epci-100m.geojson' est dans le même dossier que app.py sur GitHub
path = "epci-100m.geojson"

# Option B (Sécurité si le fichier est gros) : Vous pouvez mettre l'URL "Raw" de GitHub directement :
# path = "https://raw.githubusercontent.com/VOTRE_PSEUDO/VOTRE_DEPOT/main/epci-100m.geojson"


# =========================
# 2. LECTURE DU GEOJSON (Optimisée avec le Cache Streamlit)
# =========================
@st.cache_data
def load_geo_data(file_path):
    # Geopandas sait lire directement un fichier GeoJSON local ou distant via une URL
    gdf_raw = gpd.read_file(file_path)
    
    # On s'assure que le système de coordonnées est le bon
    if gdf_raw.crs is None:
        gdf_raw.set_crs("EPSG:4326", inplace=True)
    elif gdf_raw.crs != "EPSG:4326":
        gdf_raw = gdf_raw.to_crs("EPSG:4326")
        
    return gdf_raw

# Chargement des données
with st.spinner("Chargement des contours des EPCI..."):
    gdf = load_geo_data(path)


# =========================
# 3. BORNES DE LA FRANCE
# =========================
xmin, ymin, xmax, ymax = gdf.total_bounds


# =========================
# 4. CREATION DE LA CARTE
# =========================
m = folium.Map(
    tiles=None,          # pas de fond de carte comme sur votre code initial
    zoom_control=True
)


# =========================
# 5. ZOOM SUR LA FRANCE
# =========================
m.fit_bounds([
    [ymin, xmin],
    [ymax, xmax]
])


# =========================
# 6. BOUTON PLEIN ECRAN
# =========================
Fullscreen(
    position="topright",
    title="Plein écran",
    title_cancel="Quitter",
    force_separate_button=True
).add_to(m)


# =========================
# 7. INFO AU SURVOL (Ajusté selon les colonnes de votre GeoJSON)
# =========================
# Note : gpd.read_file charge directement les propriétés en colonnes. 
# Si dans votre fichier original les clés étaient "nom" et "code", Geopandas aura créé ces colonnes.
tooltip = folium.GeoJsonTooltip(
    fields=["nom", "code"],  # Modifié "siren" par "code" car c'était la clé d'origine dans vos propriétés
    aliases=[
        "Intercommunalité :",
        "Code SIREN :"
    ],
    sticky=True
)


# =========================
# 8. STYLE DES EPCI
# =========================
def style_function(feature):
    return {
        "fillOpacity": 0,
        "color": "black",
        "weight": 0.8
    }


# =========================
# 9. SURBRILLANCE AU SURVOL
# =========================
def highlight_function(feature):
    return {
        "fillOpacity": 0,
        "color": "red",
        "weight": 3
    }


# =========================
# 10. AJOUT DES EPCI
# =========================
folium.GeoJson(
    gdf,
    name="EPCI",
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=tooltip
).add_to(m)


# =========================
# 11. AFFICHAGE DANS STREAMLIT
# =========================
# Rendu HTML de la carte Folium dans l'application
st.components.v1.html(m._repr_html_(), height=700)
