import json
import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen
from shapely.geometry import shape
from streamlit_folium import st_folium

# Configuration de la page Streamlit
st.set_page_config(layout="wide")
st.title("Zonage Risque Inondation par Intercommunalité")
st.subheader("Score moyen de risque à l'échelle nationale")

# =========================================================================
# 1. CHARGEMENT AUTOMATIQUE ET ROBUSTE DU CSV (Depuis GitHub)
# =========================================================================


@st.cache_data
def load_csv():
    chemin_csv = "Zonage.Inondation_epci.csv"
    encodages = ["utf-8", "cp1252", "latin1"]
    df = None

    for enc in encodages:
        try:
            df = pd.read_csv(
                chemin_csv, sep=None, engine="python", encoding=enc
            )
            break
        except Exception:
            continue
    return df


with st.spinner("Chargement des scores de risque..."):
    df_score = load_csv()

if df_score is None:
    st.error(
        "Impossible de lire le fichier 'Zonage.Inondation_epci.csv'. Vérifie qu'il est bien à la racine de ton dépôt GitHub."
    )
    st.stop()

# Nettoyage automatique des espaces cachés dans le nom des colonnes
df_score.columns = df_score.columns.str.strip()

nom_colonne_score = "zonier_inondation_moyenne"
df_score[nom_colonne_score] = pd.to_numeric(
    df_score[nom_colonne_score], errors="coerce"
)

nom_colonne_code = "epci_code"
df_score[nom_colonne_code] = df_score[nom_colonne_code].astype(str)

# =========================================================================
# 2. CHARGEMENT DU GEOJSON (Depuis GitHub)
# =========================================================================


@st.cache_data
def load_geojson():
    chemin_geojson = "epci-100m.geojson"
    with open(chemin_geojson, "r", encoding="utf-8") as f:
        data = json.load(f)

    return gpd.GeoDataFrame(
        [
            {
                "epci_code": str(feat["properties"]["code"]).strip(),
                "nom": feat["properties"]["nom"],
                "geometry": shape(feat["geometry"]),
            }
            for feat in data["features"]
        ],
        crs="EPSG:4326",
    )


with st.spinner("Génération des fonds de carte géographiques..."):
    gdf = load_geojson()

# =========================================================================
# 3. FUSION SCORE + GÉOMÉTRIE
# =========================================================================
gdf = gdf.merge(df_score, on="epci_code", how="left")

# =========================================================================
# 4. CRÉATION DE LA CARTE INTERACTIVE FOLIUM
# =========================================================================
xmin, ymin, xmax, ymax = gdf.total_bounds
m = folium.Map(tiles="cartodbpositron", zoom_control=True)
m.fit_bounds([[ymin, xmin], [ymax, xmax]])

# Bouton plein écran à gauche pour éviter le conflit avec la légende
Fullscreen(
    position="topleft",
    title="Plein écran",
    title_cancel="Quitter plein écran",
    force_separate_button=True,
).add_to(m)

# Échelle de couleurs (Vert -> Jaune -> Rouge)
colormap = cm.LinearColormap(colors=["green", "yellow", "red"], vmin=1, vmax=3)


def style_function(feature):
    score = feature["properties"].get("zonier_inondation_moyenne")
    if pd.isna(score) or score is None:
        color = "#cccccc"  # Gris si donnée manquante
    else:
        color = colormap(score)

    return {
        "fillColor": color,
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.75,
    }


tooltip = folium.GeoJsonTooltip(
    fields=["nom", "epci_code", "zonier_inondation_moyenne"],
    aliases=["Nom EPCI :", "Code EPCI :", "Score inondation :"],
    sticky=True,
)

folium.GeoJson(
    gdf, style_function=style_function, tooltip=tooltip, name="EPCI Inondation"
).add_to(m)

colormap.caption = "Risque inondation (1 = faible, 3 = élevé)"
colormap.add_to(m)

# Encart du Titre HTML directement intégré à la carte
titre_html = """
<div style="
    position: fixed;
    top: 15px;
    left: 70px;
    width: 420px;
    height: 60px;
    z-index: 9999;
    font-size: 14px;
    background-color: white;
    border: 2px solid #2c7fb8;
    padding: 10px;
    border-radius: 8px;
    font-family: sans-serif;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
">
<b>Zonage inondation par EPCI</b><br>
<span style="font-size:11px; color:#555;">
Score moyen de risque (1 = faible, 3 = élevé)
</span>
</div>
"""
m.get_root().html.add_child(folium.Element(titre_html))

# =========================================================================
# 5. RENDU DE LA CARTE DANS STREAMLIT
# =========================================================================
st_folium(m, width=1100, height=650, returned_objects=[])
