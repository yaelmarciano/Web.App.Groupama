

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
# 1. TÉLÉCHARGEMENT ET EXTRACTION DU ZIP DEPUIS GOOGLE DRIVE
# ==============================================================================

# Dossier où le ZIP sera extrait sur le serveur de Streamlit
DOSSIER_EXTRACTION = "mes_donnees_ruissellement"

@st.cache_resource
def telecharger_et_extraire_donnees():
    ID_ZIP = "1veemvji7Ma-3lTHgNcNdMRL7vBK0GjH2"
    url_zip = f"https://drive.google.com/uc?export=download&id={ID_ZIP}"
    nom_fichier_zip = "ruissellement.zip"

    # 1. Téléchargement du ZIP s'il n'est pas déjà là
    if not os.path.exists(nom_fichier_zip):
        with st.spinner("Téléchargement du fichier ZIP depuis Google Drive..."):
            gdown.download(url_zip, nom_fichier_zip, quiet=False)

    # 2. Décompression de TOUS les fichiers (.TAB, .DAT, .MAP, .ID)
    if not os.path.exists(DOSSIER_EXTRACTION):
        with st.spinner("Extraction des fichiers cartographiques..."):
            with zipfile.ZipFile(nom_fichier_zip, 'r') as zip_ref:
                zip_ref.extractall(DOSSIER_EXTRACTION)

# Lancement de la préparation des fichiers
telecharger_et_extraire_donnees()

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES DEPUIS LE DOSSIER EXTRAIT
# ==============================================================================

@st.cache_data
def charger_fichiers():
    chemin_tab_final = None

    # On parcourt le dossier extrait pour trouver où est le fichier .TAB
    # (Gère automatiquement si les fichiers sont dans un sous-dossier du ZIP)
    for racine, dossiers, fichiers in os.walk(DOSSIER_EXTRACTION):
        for fichier in fichiers:
            if fichier.upper().endswith("L_AXE_RUISSEL_L_080.TAB"):
                chemin_tab_final = os.path.join(racine, fichier)
                break

    if chemin_tab_final is None:
        st.error("Le fichier L_AXE_RUISSEL_L_080.TAB est introuvable dans le dossier extrait.")
        st.stop()

    # Pyogrio va lire le fichier sur le disque, il trouvera ainsi le .DAT et le .MAP à côté !
    gdf_ruiss = gpd.read_file(chemin_tab_final, engine="pyogrio")

    # Chargement du fichier EPCI local (présent sur votre dépôt GitHub)
    gdf_epci_local = gpd.read_file("epci-100m.geojson", engine="pyogrio")

    # Conversion des coordonnées pour Folium (WGS84)
    if gdf_ruiss.crs is not None:
        gdf_ruiss = gdf_ruiss.to_crs(epsg=4326)
    if gdf_epci_local.crs is not None:
        gdf_epci_local = gdf_epci_local.to_crs(epsg=4326)

    return gdf_ruiss, gdf_epci_local

# Récupération des données prêtes
gdf_ruissellement, gdf_epci = charger_fichiers()

# ==============================================================================
# 3. CONSTRUCTION DE LA CARTE FOLIUM
# ==============================================================================

m = folium.Map(tiles="OpenStreetMap")

# Option Plein Écran
Fullscreen(
    position="topleft",
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True
).add_to(m)

# Ajout des contours des EPCI
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

# Ajout des axes de ruissellement
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

# Contrôle des couches
folium.LayerControl().add_to(m)

# ==============================================================================
# 4. AFFICHAGE INTERACTIF DANS L'APPLICATION STREAMLIT
# ==============================================================================

st_folium(m, width=1200, height=700)
