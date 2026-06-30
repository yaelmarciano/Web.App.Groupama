
import json
import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen, Search
from shapely.geometry import shape
from streamlit_folium import st_folium

# Configuration de la page Streamlit
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
    compilés à partir de la liste des arrêtés de reconnaissance de l’état de catastrophe naturelle.  
    Traitement réalisé par agrégation des arrêtés pour le péril « Inondations et / ou Coulées de Boue »  
    sur la période 2000–2026, regroupés par EPCI.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================================
# 1. CHARGEMENT DU CSV
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

    df = pd.DataFrame(data_lines, columns=["epci_code", "epci_nom", "Nombre_Arretes"])
    df["epci_code"] = df["epci_code"].astype(str)
    return df


with st.spinner("Chargement données CatNat..."):
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
        rows.append(
            {
                "siren_geojson": str(feat["properties"]["code"]).strip(),
                "nom": feat["properties"]["nom"],
                "geometry": shape(feat["geometry"]),
            }
        )

    return gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")


with st.spinner("Chargement géo..."):
    gdf = load_geojson()

# 🔥 AJOUT IMPORTANT POUR RECHERCHE
gdf["search"] = gdf["nom"].astype(str)

# =========================================================================
# 3. MERGE
# =========================================================================
gdf_final = gdf.merge(
    df_epci_counts,
    left_on="siren_geojson",
    right_on="epci_code",
    how="left"
)

gdf_final["Nombre_Arretes"] = gdf_final["Nombre_Arretes"].fillna(0).astype(int)
vrai_max = int(gdf_final["Nombre_Arretes"].max())

# =========================================================================
# 4. COULEURS (INCHANGÉES)
# =========================================================================
seuils_visuels = [0, 1, 30, 100, vrai_max]
couleurs_degrade = ["#ffffff", "#e0f3f8", "#74add1", "#313695", "#02023a"]

colormap = cm.LinearColormap(
    colors=couleurs_degrade,
    index=seuils_visuels,
    vmin=0,
    vmax=vrai_max,
)

def style_function(feature):
    val = feature["properties"]["Nombre_Arretes"]
    return {
        "fillColor": colormap(val),
        "fillOpacity": 0.85,
        "color": "#555555",
        "weight": 0.4,
    }

def highlight_function(feature):
    return {"fillOpacity": 0.7, "color": "#ff3333", "weight": 2.5}

# =========================================================================
# 5. CARTE
# =========================================================================
xmin, ymin, xmax, ymax = gdf_final.total_bounds
m = folium.Map(tiles="CartoDB positron")
m.fit_bounds([[ymin, xmin], [ymax, xmax]])

Fullscreen(position="topleft").add_to(m)

layer = folium.FeatureGroup(name="EPCI").add_to(m)

folium.GeoJson(
    gdf_final,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "siren_geojson", "Nombre_Arretes"],
        aliases=["Nom :", "SIREN :", "Arretes :"],
        sticky=True
    ),
).add_to(layer)

colormap.add_to(m)
 STREAMLIT
# =========================================================================
st_folium(m, width=1100, height=650)


