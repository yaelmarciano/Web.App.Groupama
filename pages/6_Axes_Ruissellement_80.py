import os
import zipfile
import folium
from folium.plugins import Fullscreen
import geopandas as gpd
import gdown
import streamlit as st
from streamlit_folium import st_folium

# Configuration de la page Streamlit
st.set_page_config(layout="wide")
st.title("Application de visualisation du ruissellement")

# ==============================================================================
# 1. TÉLÉCHARGEMENT DU ZIP DEPUIS GOOGLE DRIVE
# ==============================================================================


@st.cache_resource
def telecharger_donnees():
    # ID de votre fichier ZIP Google Drive
    ID_ZIP = "1veemvji7Ma-3lTHgNcNdMRL7vBK0GjH2"
    url_zip = f"https://drive.google.com/uc?export=download&id={ID_ZIP}"

    nom_fichier_zip = "ruissellement.zip"

    if not os.path.exists(nom_fichier_zip):
        with st.spinner(
            "Téléchargement du fichier ZIP depuis Google Drive..."
        ):
            gdown.download(url_zip, nom_fichier_zip, quiet=False)


# Lancement du téléchargement
telecharger_donnees()

# ==============================================================================
# 2. CHARGEMENT SANS FIONA (Utilisation native de Pyogrio + Zipfile)
# ==============================================================================


@st.cache_data
def charger_fichiers():
    nom_fichier_zip = "ruissellement.zip"

    # On utilise le gestionnaire de fichier zip standard de Python
    with zipfile.ZipFile(nom_fichier_zip, "r") as z:
        # On lit le contenu brut du fichier .TAB contenu dans l'archive
        # /!\ Attention à la casse exacte : "L_AXE_RUISSEL_L_080.TAB"
        with z.open("L_AXE_RUISSEL_L_080.TAB") as f:
            bytes_data = f.read()

        # Pyogrio est capable de lire le fichier directement depuis sa version en octets (bytes)
        # en utilisant le moteur par défaut hyper rapide
        gdf_ruiss = gpd.read_file(bytes_data, engine="pyogrio")

    # Chargement du fichier EPCI local (qui doit être dans votre GitHub)
    gdf_epci_local = gpd.read_file("epci-100m.geojson", engine="pyogrio")

    # Conversion des coordonnées pour Folium (WGS84)
    if gdf_ruiss.crs is not None:
        gdf_ruiss = gdf_ruiss.to_crs(epsg=4326)
    if gdf_epci_local.crs is not None:
        gdf_epci_local = gdf_epci_local.to_crs(epsg=4326)

    return gdf_ruiss, gdf_epci_local


# Récupération des géométries
gdf_ruissellement, gdf_epci = charger_fichiers()

# ==============================================================================
# 3. CONSTRUCTION DE LA CARTE FOLIUM
# ==============================================================================

m = folium.Map(tiles="OpenStreetMap")

# Mode Plein Écran
Fullscreen(
    position="topleft",
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True,
).add_to(m)

# Ajout de la couche EPCI
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
        fields=["nom", "code"],
        aliases=["Nom de l'EPCI :", "Numéro :"],
        localize=True,
    ),
).add_to(m)

# Ajout de la couche des axes de ruissellement
folium.GeoJson(
    gdf_ruissellement,
    name="Axes de ruissellement",
    style_function=lambda x: {"color": "#0000FF", "weight": 2.5},
).add_to(m)

# Zoom automatique sur les données de ruissellement
m.fit_bounds(gdf_ruissellement.total_bounds.tolist())

# Menu de gestion des couches
folium.LayerControl().add_to(m)

# ==============================================================================
# 4. AFFICHAGE DANS L'APPLICATION STREAMLIT
# ==============================================================================

st_folium(m, width=1200, height=700)
