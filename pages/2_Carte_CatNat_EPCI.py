
import json
import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen, Search
from shapely.geometry import shape
from streamlit_folium import st_folium

# =========================================================================
# CONFIG STREAMLIT
# =========================================================================
st.set_page_config(layout="wide")
st.title("Carte interactive des arrêtés CatNat par Intercommunalité")
st.subheader("Période 2000-2026 | Péril : Inondations et Coulées de Boue")

st.markdown(
    """
    <div style="
        font-size:12px;
        color:#666;
        margin-bottom:10px;
        line-height:1.4;
    ">
    Données : arrêtés CatNat issus de la base officielle CCR (Caisse Centrale de Réassurance), 
    regroupés pour le péril « Inondations et / ou Coulées de Boue » sur la période 2000–2026.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# 1. CSV
# =========================================================================
@st.cache_data
def load_csv():
    chemin_csv = "catnat.par_epci.csv"
    data_lines = []
    encodages = ["utf-8", "cp1252", "latin1"]

    for enc in encodages:
        try:
            with open(chemin_csv, "r", encoding=enc) as f:
                lines = f.readlines()
            break
        except Exception:
            continue

    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) >= 3:
            code = parts[0].replace('"', "").strip()
            nb = parts[-1].strip()
            nom = ",".join(parts[1:-1]).replace('"', "").strip()
            data_lines.append([code, nom, int(nb) if nb.isdigit() else 0])

    return pd.DataFrame(
        data_lines, columns=["epci_code", "epci_nom", "Nombre_Arretes"]
    )

df_epci_counts = load_csv()

# =========================================================================
# 2. GEOJSON
# =========================================================================
@st.cache_data
def load_geojson():
    with open("epci-100m.geojson", "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for feat in data["features"]:
        rows.append({
            "siren_geojson": str(feat["properties"]["code"]).strip(),
            "nom": feat["properties"]["nom"],
            "geometry": shape(feat["geometry"]),
        })

    return gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")

gdf = load_geojson()

# =========================================================================
# MERGE
# =========================================================================
gdf_final = gdf.merge(
    df_epci_counts,
    left_on="siren_geojson",
    right_on="epci_code",
    how="left"
)

gdf_final["Nombre_Arretes"] = gdf_final["Nombre_Arretes"].fillna(0).astype(int)

# 🔥 champ de recherche (AJOUT)
gdf_final["search"] = gdf_final["nom"].astype(str)

# =========================================================================
# MAP
# =========================================================================
xmin, ymin, xmax, ymax = gdf_final.total_bounds

m = folium.Map(tiles="CartoDB positron", zoom_control=True)
m.fit_bounds([[ymin, xmin], [ymax, xmax]])

Fullscreen(position="topleft").add_to(m)

# =========================================================================
# STYLE
# =========================================================================
def style_function(feature):
    val = feature["properties"]["Nombre_Arretes"]
    return {
        "fillColor": colormap(val),
        "fillOpacity": 0.85 if val > 0 else 0.1,
        "color": "#555555",
        "weight": 0.4,
    }

def highlight_function(feature):
    return {"fillOpacity": 0.7, "color": "#ff3333", "weight": 2.5}

vrai_max = gdf_final["Nombre_Arretes"].max()

colormap = cm.LinearColormap(
    colors=["#ffffff", "#e0f3f8", "#74add1", "#313695", "#02023a"],
    vmin=0,
    vmax=vrai_max,
    caption="CatNat"
)

tooltip = folium.GeoJsonTooltip(
    fields=["nom", "siren_geojson", "Nombre_Arretes"],
    aliases=["Nom :", "SIREN :", "Arrêtés :"],
)

# =========================================================================
# LAYER
# =========================================================================
layer = folium.GeoJson(
    gdf_final,
    name="EPCI",
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=tooltip,
).add_to(m)

colormap.add_to(m)

# =========================================================================
# 🔎 BARRE DE RECHERCHE (AJOUT SIMPLE)
# =========================================================================
Search(
    layer=layer,
    search_label="nom",
    geom_type="Polygon",
    placeholder="Rechercher un EPCI (nom uniquement)",
    collapsed=False
).add_to(m)

# =========================================================================
# TITRE CARTE
# =========================================================================
titre_html = """
<div style="position: fixed; top: 15px; left: 70px; z-index:9999;
background:white; padding:8px; border-radius:6px; font-size:13px;">
<b>CatNat 2000–2026</b><br>
Inondations & Coulées de Boue
</div>
"""
m.get_root().html.add_child(folium.Element(titre_html))

# =========================================================================
# STREAMLIT
# =========================================================================
st_folium(m, width=1100, height=650, returned_objects=[])
