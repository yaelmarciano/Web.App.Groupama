import os
import zipfile
import urllib.request
import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

# 1. Toujours configurer la page en premier
st.title("Axes de ruissellement (Département 80)")

# Noms des dossiers locaux (propres à cette page)
NOM_ZIP = "ruissellement_80.zip"
DOSSIER_CARTOS = "fichiers_mappage_80"

# ==============================================================================
# FONCTION DE TÉLÉCHARGEMENT ISOLÉE
# ==============================================================================
@st.cache_resource
def telecharger_donnees_drive():
    # Votre ID de fichier Google Drive exact
    FILE_ID = "1veemvji7Ma-3lTHgNcNdMRL7vBK0GjH2"
    url_drive = f"https://docs.google.com/uc?export=download&id={FILE_ID}&confirm=t"
    
    try:
        # Si le fichier n'est pas déjà sur le serveur, on le télécharge
        if not os.path.exists(NOM_ZIP):
            # Configuration d'un agent pour simuler un navigateur internet ordinaire
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url_drive, NOM_ZIP)
            
        # Si le dossier d'extraction n'existe pas, on extrait tout le ZIP
        if not os.path.exists(DOSSIER_CARTOS):
            with zipfile.ZipFile(NOM_ZIP, 'r') as zip_ref:
                zip_ref.extractall(DOSSIER_CARTOS)
        return True
    except Exception as e:
        # On affiche l'erreur uniquement ici sans faire planter l'application
        st.warning(f"Note : Impossible de récupérer les données depuis Google Drive pour le moment ({e}).")
        return False

# Lancement du téléchargement en arrière-plan
donnees_disponibles = telecharger_donnees_drive()

# ==============================================================================
# CHARGEMENT DES COUCHES SI TOUT EST PRÊT
# ==============================================================================
if donnees_disponibles:
    try:
        # Trouver le chemin exact du fichier .TAB (même s'il est dans un sous-dossier)
        chemin_tab = None
        for racine, dossiers, fichiers in os.walk(DOSSIER_CARTOS):
            for f in fichiers:
                if f.upper().endswith("L_AXE_RUISSEL_L_080.TAB"):
                    chemin_tab = os.path.join(racine, f)
                    break
        
        if chemin_tab and os.path.exists(chemin_tab):
            # Chargement classique avec GeoPandas
            gdf_ruissellement = gpd.read_file(chemin_tab)
            
            # Conversion des coordonnées pour Folium
            if gdf_ruissellement.crs is not None:
                gdf_ruissellement = gdf_ruissellement.to_crs(epsg=4326)
                
            # --- Création de la carte Folium ---
            m = folium.Map(tiles="OpenStreetMap")
            
            # Ajout des axes de ruissellement
            folium.GeoJson(
                gdf_ruissellement, 
                name="Axes de ruissellement",
                style_function=lambda x: {"color": "#0000FF", "weight": 2.5}
            ).add_to(m)
            
            # Zoom automatique sur vos données
            m.fit_bounds(gdf_ruissellement.total_bounds.tolist())
            
            # Optionnel : Essayer de charger l'EPCI si présent sur votre GitHub
            if os.path.exists("epci-100m.geojson"):
                try:
                    gdf_epci = gpd.read_file("epci-100m.geojson")
                    if gdf_epci.crs is not None:
                        gdf_epci = gdf_epci.to_crs(epsg=4326)
                    folium.GeoJson(
                        gdf_epci,
                        name="Contours des EPCI",
                        style_function=lambda x: {"fillColor": "transparent", "color": "#666666", "weight": 1.5}
                    ).add_to(m)
                except:
                    pass # Si l'EPCI plante, on l'ignore pour ne pas bloquer la carte principale
            
            # Affichage de la carte dans Streamlit
            st_folium(m, width=1100, height=600, key="carte_ruissellement_unique")
            
        else:
            st.info("Le fichier 'L_AXE_RUISSEL_L_080.TAB' n'a pas encore été trouvé dans l'archive décompressée.")
            
    except Exception as e:
        st.error(f"Une erreur est survenue lors de l'affichage de cette carte : {e}")
else:
    st.info("Sécurisation de l'application : Chargement de la carte des axes de ruissellement en attente.")
