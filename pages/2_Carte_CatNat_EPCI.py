
import json
import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen, Search   # ✅ AJOUT ICI
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

    header = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) >= 3:
            code = parts[0].replace('"', "").strip()
            nb = parts[-1].strip()
            nom = ",".join(parts[1:-1]).replace('"', "").strip()

            if header is None:
                header = (code, nom, nb)
            else:
                data_lines.append([code, nom, int(nb) if nb.isdigit() else 0])

    return pd.DataFrame(data_lines, columns=["epci_code", "epci_nom", "Nombre_Arretes"])


with st.spinner("Analyse du fichier de données CatNat..."):
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


with st.spinner("Génération des fonds géographiques..."):
    gdf = load_geojson()

# =========================================================================
# 3. FUSION
# =========================================================================

gdf_final = gdf.merge(
    df_epci_counts,
    left_on="siren_geojson",
    right_on="epci_code",
    how="left"
)

gdf_final["Nombre_Arretes"] = gdf_final["Nombre_Arretes"].fillna(0).astype(int)

# ⭐⭐⭐ AJOUT IMPORTANT POUR RECHERCHE ⭐⭐⭐
gdf_final["search"] = gdf_final["nom"].astype(str) + " " + gdf_final["siren_geojson"].astype(str)

# =========================================================================
# 4. CARTE
# =========================================================================

xmin, ymin, xmax, ymax = gdf_final.total_bounds

m = folium.Map(tiles="CartoDB positron", zoom_control=True)
m.fit_bounds([[ymin, xmin], [ymax, xmax]])

Fullscreen(position="topleft").add_to(m)

# =========================================================================
# 5. STYLE
# =========================================================================

colormap = cm.LinearColormap(
    colors=["#ffffff", "#e0f3f8", "#74add1", "#313695", "#02023a"],
    vmin=0,
    vmax=max(gdf_final["Nombre_Arretes"])
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
    return {"fillOpacity": 0.7, "color": "red", "weight": 2.5}

# =========================================================================
# 6. COUCHE EPCI (IMPORTANT : layer pour Search)
# =========================================================================

layer_epci = folium.FeatureGroup(name="EPCI").add_to(m)

folium.GeoJson(
    gdf_final,
    name="EPCI",
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "siren_geojson", "Nombre_Arretes"],
        aliases=["Nom :", "SIREN :", "Arrêtés :"]
    ),
).add_to(layer_epci)

colormap.add_to(m)

# =========================================================================
# 7. 🔎 BARRE DE RECHERCHE (ZOOM AUTOMATIQUE)
# =========================================================================

Search(
    layer=layer_epci,
    geom_type="Polygon",
    placeholder="Rechercher un EPCI (entrez le nom)",
    search_label="search",
    collapsed=False
).add_to(m)

# =========================================================================
# 8. TITRE HTML (inchangé)
# =========================================================================

titre_html = """
<div style="position: fixed; 
            top: 15px; left: 70px; width: 460px; 
            z-index:9999; font-size:14px; background-color: white;
            border:2px solid #313695; padding: 8px; border-radius: 6px;">
<b>Nombre d'arrêtés CatNat par Intercommunalité (EPCI)</b><br>
<span style="font-size:11px; color:#555;">
Période 2000-2026 | Inondations & Coulées de Boue
</span>
</div>
"""
m.get_root().html.add_child(folium.Element(titre_html))

# =========================================================================
# 9. STREAMLIT
# =========================================================================

st_folium(m, width=1100, height=650, returned_objects=[])
