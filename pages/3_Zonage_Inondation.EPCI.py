import json
import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen
from shapely.geometry import shape
from streamlit_folium import st_folium
from folium.plugins import Fullscreen, Search

# =========================================================================
# CONFIG STREAMLIT
# =========================================================================
st.set_page_config(layout="wide")
st.title("Zonage Risque Inondation par Intercommunalité")
st.subheader("Score moyen de risque à l'échelle nationale")
st.markdown(
    """
    <div style="
        font-size:12px;
        color:#666;
        margin-bottom:10px;
        line-height:1.4;
    ">
    Données : zonage interne Groupama du risque inondation à la maille IRIS.  
    Les scores ont été agrégés par moyenne à la maille communale, puis à la maille intercommunale (EPCI) afin de produire un indicateur homogène de risque à l’échelle nationale.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# 1. CSV
# =========================================================================
@st.cache_data
def load_csv():
    chemin_csv = "Zonage.Inondation_epci.csv"
    encodages = ["utf-8", "cp1252", "latin1"]
    df = None

    for enc in encodages:
        try:
            df = pd.read_csv(chemin_csv, sep=None, engine="python", encoding=enc)
            break
        except Exception:
            continue
    return df


df_score = load_csv()

if df_score is None:
    st.error("Impossible de lire le CSV")
    st.stop()

df_score.columns = df_score.columns.str.strip()

nom_colonne_score = "zonier_inondation_moyenne"
df_score[nom_colonne_score] = pd.to_numeric(df_score[nom_colonne_score], errors="coerce")

df_score["epci_code"] = df_score["epci_code"].astype(str)

# =========================================================================
# 2. GEOJSON
# =========================================================================
@st.cache_data
def load_geojson():
    with open("epci-100m.geojson", "r", encoding="utf-8") as f:
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


gdf = load_geojson()

# =========================================================================
# 3. FUSION
# =========================================================================
gdf = gdf.merge(df_score, on="epci_code", how="left")

# =========================================================================
# 4. CARTE
# =========================================================================
xmin, ymin, xmax, ymax = gdf.total_bounds

m = folium.Map(tiles="cartodbpositron", zoom_control=True)
m.fit_bounds([[ymin, xmin], [ymax, xmax]])

Fullscreen(position="topleft").add_to(m)

colormap = cm.LinearColormap(colors=["green", "yellow", "red"], vmin=1, vmax=3)

# =========================================================================
# 5. STYLE + HIGHLIGHT (IMPORTANT ICI)
# =========================================================================
def style_function(feature):
    score = feature["properties"].get("zonier_inondation_moyenne")

    if pd.isna(score) or score is None:
        color = "#cccccc"
    else:
        color = colormap(score)

    return {
        "fillColor": color,
        "color": "#444444",
        "weight": 0.6,
        "fillOpacity": 0.75,
    }


# 🔥 CONTOUR ROUGE AU SURVOL / CLIC VISUEL
def highlight_function(feature):
    return {
        "color": "#FF0000",
        "weight": 3,
        "fillOpacity": 0.85,
    }


tooltip = folium.GeoJsonTooltip(
    fields=["nom", "epci_code", "zonier_inondation_moyenne"],
    aliases=["Nom EPCI :", "Code EPCI :", "Score inondation :"],
    sticky=True,
)

folium.GeoJson(
    gdf,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=tooltip,
    name="EPCI Inondation",
).add_to(m)

colormap.caption = "Risque inondation (1 = faible, 3 = élevé)"
colormap.add_to(m)

# =========================================================================
# 6. TITRE CARTE
# =========================================================================
titre_html = """
<div style="
    position: fixed;
    top: 15px;
    left: 70px;
    width: 420px;
    z-index: 9999;
    font-size: 14px;
    background: white;
    border: 2px solid #2c7fb8;
    padding: 10px;
    border-radius: 8px;
">
<b>Zonage inondation par EPCI</b><br>
<span style="font-size:11px; color:#555;">
Score moyen de risque (1 = faible, 3 = élevé)
</span>
</div>
"""

m.get_root().html.add_child(folium.Element(titre_html))

# =========================================================================
# 7. AFFICHAGE STREAMLIT
# =========================================================================
st_folium(m, width=1100, height=650, returned_objects=[])
