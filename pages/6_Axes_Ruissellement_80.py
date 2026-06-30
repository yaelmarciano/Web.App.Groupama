

import os
import zipfile
import folium
from folium.plugins import Fullscreen
import geopandas as gpd
import gdown
import streamlit as st
from streamlit_folium import st_folium

# Configuration de la page Streamlit (Largeur maximale)
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

    # On télécharge le fichier seulement s'il n'existe pas encore localement
    if not os.path.exists(nom_fichier_zip):
        with st.spinner(
            "Téléchargement du fichier ZIP depuis Google Drive..."
        ):
            gdown.download(url_zip, nom_fichier_zip, quiet=False)


# Lancement du téléchargement automatique
telecharger_donnees()

# ==============================================================================
# 2. CHARGEMENT SANS FIONA (Scan intelligent du ZIP + Moteur Pyogrio)
# ==============================================================================


@st.cache_data
def charger_fichiers():
    nom_fichier_zip = "ruissellement.zip"
    chemin_tab_interne = None

    # On ouvre le fichier ZIP en mémoire
    with zipfile.ZipFile(nom_fichier_zip, "r") as z:
        # Récupération de la liste de tout ce qui se trouve dans le ZIP
        liste_fichiers = z.namelist()

        # On cherche dynamiquement le fichier qui se termine par L_AXE_RUISSEL_L_080.TAB
        # (Peu importe s'il est dans un sous-dossier ou écrit en minuscules)
        for f in liste_fichiers:
            if f.upper().endswith("L_AXE_RUISSEL_L_080.TAB"):
                chemin_tab_interne = f
                break

        # Si le code ne trouve rien, on affiche une erreur propre avec la liste des fichiers
        if chemin_tab_interne is None:
            st.error(
                f"Le fichier L_AXE_RUISSEL_L_080.TAB est introuvable dans l'archive ZIP. "
                f"Contenu détecté dans le ZIP : {liste_fichiers}"
            )
            st.stop()

        # On extrait les octets du fichier trouvé
        with z.open(chemin_tab_interne) as f:
            bytes_data = f.read()

        # Lecture ultra-rapide des octets bruts avec Pyogrio
        gdf_ruiss = gpd.read_file(bytes_data, engine="pyogrio")

    # Chargement du fichier EPCI local (présent sur votre dépôt GitHub)
    gdf_epci_local = gpd.read_file("epci-100m.geojson", engine="pyogrio")

    # Conversion des coordonnées des deux couches pour Folium (WGS84)
    if gdf_ruiss.crs is not None:
        gdf_ruiss = gdf_ruiss.to_crs(epsg=4326)
    if gdf_epci_local.crs is not None:
        gdf_epci_local = gdf_epci_local.to_crs(epsg=4326)

    return gdf_ruiss, gdf_epci_local


# Récupération des données prêtes à être cartographiées
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
    force_separate_button=True,
).add_to(m)

# Ajout de la couche des contours des EPCI
folium.GeoJson(
    gdf_epci,
    name="Contours des EPCI",
    style_function=lambda x: {
        "fillColor": "transparent",
        "color": "#666666",  # Gris
        "weight": 1.5,
    },
    highlight_function=lambda x: {
        "fillColor": "#FF0000",  # Rouge transparent au survol
        "fillOpacity": 0.2,
        "color": "#FF0000",  # Ligne rouge vif
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
    style_function=lambda x: {"color": "#0000FF", "weight": 2.5},  # Bleu eau
).add_to(m)

# Centrage automatique de la carte sur vos axes de ruissellement
m.fit_bounds(gdf_ruissellement.total_bounds.tolist())

# Menu de contrôle des couches (Cocher/Décocher en haut à droite)
folium.LayerControl().add_to(m)

# ==============================================================================
# 4. AFFICHAGE INTERACTIF DANS L'APPLICATION STREAMLIT
# ==============================================================================

st_folium(m, width=1200, height=700)
