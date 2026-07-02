
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen

# Configuration de la page Streamlit
st.set_page_config(page_title="Atlas Risque Inondation", layout="wide")
st.title("Cartographie Interactive des Axes de Ruissellement par EPCI")

# 1. Définition des chemins de données
# Le GeoJSON est dans le même dossier sur GitHub :
CHEMIN_EPCI = "epci-100m.geojson"

# Le gros fichier TAB reste sur ton Google Drive public :
URL_DRIVE_RUISSELLEMENT = "https://drive.google.com/file/d/18Qa9kk8ZR54n22w7uGWSHcwje_j-v1Uq/view?usp=sharing"

@st.cache_data # Évite de recharger les fichiers à chaque clic
def charger_donnees():
    # Chargement du GeoJSON local (moteur pyogrio pour la stabilité sur Streamlit)
    gdf_epci = gpd.read_file(CHEMIN_EPCI, engine="pyogrio")
    
    # Chargement des axes depuis Google Drive
    gdf_ruissellement = gpd.read_file(URL_DRIVE_RUISSELLEMENT, engine="pyogrio")
    
    # Conversion forcée en WGS84 (le système requis par Folium)
    if gdf_ruissellement.crs is not None:
        gdf_ruissellement = gdf_ruissellement.to_crs(epsg=4326)
    if gdf_epci.crs is not None:
        gdf_epci = gdf_epci.to_crs(epsg=4326)
        
    return gdf_epci, gdf_ruissellement

# Chargement sécurisé avec indicateur visuel
with st.spinner("Chargement des cartes en cours..."):
    try:
        gdf_epci, gdf_ruissellement = charger_donnees()
        st.success("Données géographiques chargées avec succès !")
    except Exception as e:
        st.error(f"Erreur technique lors du chargement : {e}")
        st.stop()

# 2. Construction de la carte interactive
m = folium.Map(tiles="OpenStreetMap")

# Ajout du bouton Plein Écran
Fullscreen(
    position="topleft",
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True
).add_to(m)

# Couche 1 : Les contours des EPCI (rouge au survol)
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
        "fillOpacity": 0.15,    
        "color": "#FF0000",    
        "weight": 3.0,         
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['nom', 'code'], # Vérifie bien que ces colonnes exactes existent dans ton GeoJSON
        aliases=['Nom de l\'EPCI :', 'Code Territoire :'],
        localize=True
    )
).add_to(m)

# Couche 2 : Les axes de ruissellement (lignes bleues par-dessus)
folium.GeoJson(
    gdf_ruissellement, 
    name="Axes de ruissellement",
    style_function=lambda x: {
        "color": "#0022FF",  
        "weight": 2.5
    }
).add_to(m)

# Centrage automatique et dynamique du zoom sur tes données
m.fit_bounds(gdf_ruissellement.total_bounds.tolist())

# Menu des couches en haut à droite
folium.LayerControl().add_to(m)

# 3. Affichage dans l'interface Streamlit
st_folium(m, width=1300, height=650)
