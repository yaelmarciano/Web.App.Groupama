import os
import zipfile
import urllib.request
import folium
from folium.plugins import Fullscreen
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

# Configuration de la page
st.set_page_config(layout="wide")
st.title("Application de visualisation du ruissellement")

# Chemins locaux sur le serveur Streamlit
NOM_ZIP = "ruissellement.zip"
DOSSIER_CIBLE = "pack_mapinfo"

# ==============================================================================
# 1. TÉLÉCHARGEMENT ET EXTRACTION SÉCURISÉS (FONCTIONS NATIVES)
# ==============================================================================

@st.cache_resource
def preparer_fichiers_geographiques():
    # Lien de téléchargement direct de votre ZIP Google Drive
    FILE_ID = "1veemvji7Ma-3lTHgNcNdMRL7vBK0GjH2"
    url_drive = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
    
    try:
        # Téléchargement du ZIP si absent
        if not os.path.exists(NOM_ZIP):
            with st.spinner("Téléchargement des axes de ruissellement depuis Google Drive..."):
                urllib.request.urlretrieve(url_drive, NOM_ZIP)
        
        # Extraction du ZIP si le dossier n'existe pas encore
        if not os.path.exists(DOSSIER_CIBLE):
            with zipfile.ZipFile(NOM_ZIP, 'r') as zip_ref:
                zip_ref.extractall(DOSSIER_CIBLE)
        return True
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return False

# Exécution de la préparation
fichiers_prets = preparer_fichiers_geographiques()

# ==============================================================================
# 2. CHARGEMENT ET TRAITEMENT DES COUCHES
# ==============================================================================

gdf_ruissellement = None
gdf_epci = None

if fichiers_prets:
    try:
        # Recherche du fichier .TAB (gère si c'est dans un sous-dossier du ZIP)
        chemin_tab = None
        for racine, dossiers, fichiers in os.walk(DOSSIER_CIBLE):
            for f in fichiers:
                if f.upper().endswith("L_AXE_RUISSEL_L_080.TAB"):
                    chemin_tab = os.path.join(racine, f)
                    break
        
        # Chargement de la couche Ruissellement
        if chemin_tab:
            gdf_ruissellement = gpd.read_file(chemin_tab)
            if gdf_ruissellement.crs is not None:
                gdf_ruissellement = gdf_ruissellement.to_crs(epsg=4326)
        else:
            st.warning("Fichier .TAB introuvable dans le dossier extrait.")
            
    except Exception as e:
        st.warning(f"Impossible de charger les axes de ruissellement : {e}")

# Chargement sécurisé de l'EPCI (vérifie s'il est bien sur votre GitHub)
if os.path.exists("epci-100m.geojson"):
    try:
        gdf_epci = gpd.read_file("epci-100m.geojson")
        if gdf_epci.crs is not None:
            gdf_epci = gdf_epci.to_crs(epsg=4326)
    except Exception as e:
        st.warning(f"Erreur de lecture du fichier EPCI : {e}")
else:
    st.info("ℹ️ Le fichier 'epci-100m.geojson' n'est pas détecté à la racine de GitHub.")

# ==============================================================================
# 3. AFFICHAGE DE LA CARTE (SANS TOUT BLOQUER)
# ==============================================================================

# On crée une carte de base quoi qu'il arrive
m = folium.Map(tiles="OpenStreetMap")
Fullscreen(position="topleft", force_separate_button=True).add_to(m)

carte_a_des_donnees = False

# Ajout EPCI si disponible
if gdf_epci is not None:
    folium.GeoJson(
        gdf_epci,
        name="Contours des EPCI",
        style_function=lambda x: {"fillColor": "transparent", "color": "#666666", "weight": 1.5},
        highlight_function=lambda x: {"fillColor": "#FF0000", "fillOpacity": 0.2, "color": "#FF0000", "weight": 3.0},
        tooltip=folium.GeoJsonTooltip(fields=['nom', 'code'], aliases=['Nom :', 'Numéro :'], localize=True)
    ).add_to(m)
    carte_a_des_donnees = True

# Ajout Ruissellement si disponible
if gdf_ruissellement is not None:
    folium.GeoJson(
        gdf_ruissellement, 
        name="Axes de ruissellement",
        style_function=lambda x: {"color": "#0000FF", "weight": 2.5}
    ).add_to(m)
    m.fit_bounds(gdf_ruissellement.total_bounds.tolist())
    carte_a_des_donnees = True

folium.LayerControl().add_to(m)

# Rendu de la carte dans Streamlit
if carte_a_des_donnees:
    st_folium(m, width=1200, height=700)
else:
    st.write("En attente du chargement des données géographiques...")
