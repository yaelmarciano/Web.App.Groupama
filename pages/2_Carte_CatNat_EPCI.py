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
# STREAMLIT
# =========================================================================
st.set_page_config(layout="wide")

st.title("Carte interactive des arrêtés CatNat par Intercommunalité")
st.subheader("Période 2000-2026 | Péril : Inondations et Coulées de Boue")

st.markdown(
    """
    <div style="font-size:12px;color:#666;margin-bottom:10px;line-height:1.4;">
    Données : arrêtés CatNat CCR agrégés par EPCI sur la période 2000–2026.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# CSV
# =========================================================================
@st.cache_data
def load_csv():
    with open("catnat.par_epci.csv", "r", encoding="utf-8") as f:
        lines = f.readlines()

    data = []
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) >= 3:
            code = parts[0].replace('"', "").strip()
            nb = parts[-1].strip()
            nom = ",".join(parts[1:-1]).replace('"', "").strip()
            data.append([code, nom, int(nb) if nb.isdigit() else 0])

    return pd.DataFrame(data, columns=["epci_code", "epci_nom", "Nombre_Arretes"])


df_epci_counts = load_csv()

# =========================================================================
# GEOJSON + 🔥 IMPORTANT SEARCH FIELD
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
            "geometry": shape(feat["geometry"])
        })

    gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")

    # ⭐ IMPORTANT POUR SEARCH (comme ton code qui marchait)
    gdf["search"] = gdf["nom"].astype(str) + " " + gdf["siren_geojson"].astype(str)

    return gdf


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

# =========================================================================
# COULEURS (INCHANGÉES)
# =========================================================================
vmax = int(gdf_final["Nombre_Arretes"].max()) if len(gdf_final) > 0 else 100

colormap = cm.LinearColormap(
    colors=["#ffffff", "#e0f3f8", "#74add1", "#313695", "#02023a"],
    vmin=0,
    vmax=vmax,
    caption="CatNat"
)

def style_function(feature):
    v = feature["properties"]["Nombre_Arretes"]
    return {
        "fillColor": colormap(v),
        "fillOpacity": 0.85 if v > 0 else 0.1,
        "color": "#555",
        "weight": 0.4,
    }

def highlight_function(feature):
    return {"color": "red", "weight": 3, "fillOpacity": 0.7}

# =========================================================================
# MAP
# =========================================================================
xmin, ymin, xmax, ymax = gdf_final.total_bounds

m = folium.Map(tiles="CartoDB positron")
m.fit_bounds([[ymin, xmin], [ymax, xmax]])

Fullscreen().add_to(m)

# =========================================================================
# ⭐ FEATURE GROUP (OBLIGATOIRE POUR SEARCH QUI MARCHE)
# =========================================================================
layer = folium.FeatureGroup(name="EPCI").add_to(m)

geo = folium.GeoJson(
    gdf_final,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "siren_geojson", "Nombre_Arretes"],
        aliases=["Nom :", "Code :", "CatNat :"],
        sticky=True
    )
).add_to(layer)

# =========================================================================
# 🔎 SEARCH QUI MARCHE (COMME TON CODE EPCI)
# =========================================================================
Search(
    layer=layer,
    search_label="search",
    placeholder="Rechercher une intercommunalité",
    collapsed=False
).add_to(m)

colormap.add_to(m)

# =========================================================================
# TITRE
# =========================================================================
titre_html = """
<div style="position: fixed; top: 15px; left: 70px; z-index:9999;
background:white;padding:10px;border-radius:6px;font-family:Arial;">
<b>CatNat 2000-2026</b><br>
<span style="font-size:11px;">CCR / EPCI</span>
</div>
"""
m.get_root().html.add_child(folium.Element(titre_html))

# =========================================================================
# OUTPUT
# =========================================================================
st_folium(m, width=1100, height=650)
