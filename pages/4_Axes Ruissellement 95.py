import folium
import geopandas as gpd
from folium.plugins import Fullscreen
from folium.plugins import Fullscreen, Search

# ==========================================
# 1. CHARGEMENT ET PRÉPARATION DES DONNÉES
# ==========================================

print("Chargement des axes de ruissellement...")
# --- Données 1 : Les Axes de Ruissellement ---
gdf_axes = gpd.read_file("L_AXES_RUISSELEMENTS_095.shp")

# Correction de l'erreur JSON pour les axes
for col in gdf_axes.select_dtypes(
    include=["datetime64", "datetime", "object"]
).columns:
    if hasattr(gdf_axes[col], "dt"):
        gdf_axes[col] = gdf_axes[col].astype(str)

# Conversion en degrés pour Folium
gdf_axes_4326 = gdf_axes.to_crs(epsg=4326)
print("Chargement des contours EPCI...")
# --- Données 2 : Les Contours EPCI ---
try:
    gdf_epci = gpd.read_file("epci-100m.geojson", engine="fiona")
except Exception:
    gdf_epci = gpd.read_file("epci-100m.geojson")

# Conversion en degrés pour Folium
gdf_epci_4326 = gdf_epci.to_crs(epsg=4326)

# On s'assure que les colonnes 'nom' et 'code' (siren) existent bien pour le tooltip
# Si ton fichier a des noms de colonnes un peu différents, on les renomme à la volée
if "code" in gdf_epci_4326.columns and "siren" not in gdf_epci_4326.columns:
    gdf_epci_4326 = gdf_epci_4326.rename(columns={"code": "siren"})
    gdf_epci_4326["nom"] = gdf_epci_4326["nom"].astype(str)
    gdf_epci_4326["siren"] = gdf_epci_4326["siren"].astype(str)
    gdf_epci_4326["search"] = gdf_epci_4326["nom"] + " " + gdf_epci_4326["siren"]


# ==========================================
# 2. CONFIGURATION DE LA CARTE
# ==========================================

print("Création de la carte...")
# Calcul du centre basé sur les axes de ruissellement
centre_origine = gdf_axes.geometry.centroid
centre_4326 = centre_origine.to_crs(epsg=4326)
centre = [centre_4326.y.mean(), centre_4326.x.mean()]

# Création de la carte en grand format
m = folium.Map(location=centre, zoom_start=11, width="100%", height="100%")

# Ajout du bouton Plein écran
Fullscreen(
    position="topleft",
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True,
).add_to(m)
# ==========================================
# 3. CONFIGURATION DES STYLES ET TOOLTIPS (INSPIRÉ DE DATABRICKS)
# ==========================================

# Bulle d'information au survol des EPCI
tooltip_epci = folium.GeoJsonTooltip(
    fields=["nom", "siren"],
    aliases=["Intercommunalité :", "Code SIREN :"],
    sticky=True,
)


# Style normal : contours noirs fins et transparents
def style_epci(feature):
    return {"fillOpacity": 0, "color": "black", "weight": 0.8}


# Style au survol : devient rouge et plus épais
def highlight_epci(feature):
    return {"fillOpacity": 0, "color": "red", "weight": 3}


# ==========================================
# 4. SUPERPOSITION DES COUCHES
# ==========================================

# Couche 1 : Les contours des EPCI (Style noir, surbrillance rouge et Tooltip inclus)
geojson_epci = folium.GeoJson(
    gdf_epci_4326,
    name="Contours EPCI",
    style_function=style_epci,
    highlight_function=highlight_epci,
    tooltip=tooltip_epci,
).add_to(m)
# Couche 2 : Les axes de ruissellement (En bleu par-dessus)
folium.GeoJson(
    gdf_axes_4326,
    name="Axes de Ruissellement",
    style_function=lambda x: {
        "color": "blue",
        "weight": 1.5,
    },
).add_to(m)
Search(
    layer=geojson_epci,
    geom_type="Polygon",
    placeholder=" 🔎 Rechercher un EPCI (entrez le nom)",
    search_label="search",
    collapsed=False,
).add_to(m)
# Menu des couches en haut à droite
folium.LayerControl().add_to(m)

print("Carte prête !")
# ==========================================
# 5. AFFICHAGE
# ==========================================
import streamlit as st
from streamlit_folium import st_folium

# Affichage propre dans Streamlit
st.title("Carte des Axes de Ruissellement du Val d'Oise (95)")
st.markdown(
    """
    <div style="
        font-size:12px;
        color:#666;
        margin-bottom:12px;
        line-height:1.4;
    ">
    Données : axes de ruissellement du département du <b>Val-d'Oise (95)</b>, issus du jeu de données <i>« Axes de ruissellement »</i> diffusé sur <b>data.gouv.fr</b>. Les axes représentent les principaux chemins d'écoulement des eaux de pluie, où le risque de ruissellement est le plus marqué.
    </div>
    """,
    unsafe_allow_html=True
)
st_folium(m, width=800, height=600, use_container_width=True)
