import json
import streamlit as st
import folium
import branca.colormap as cm
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

# ==============================================================================
# 1. PAGE STREAMLIT
# ==============================================================================
st.set_page_config(layout="wide")
st.title("Exposition au risque de ruissellement")

# ==============================================================================
# 2. CHARGEMENT GEOJSON (SANS GEOPANDAS => donc pas de shapely/pyproj/fiona)
# ==============================================================================
@st.cache_data
def load_geojson():
    with open("departements.geojson", "r", encoding="utf-8") as f:
        departements = json.load(f)

    with open("epci-100m.geojson", "r", encoding="utf-8") as f:
        epci = json.load(f)

    return departements, epci


departements_geojson, epci_geojson = load_geojson()

# ==============================================================================
# 3. DONNÉES (codes département → valeurs)
# ==============================================================================
departement_values = {
    "59": 104, "62": 104, "02": 104, "08": 104, "57": 104, "67": 104,
    "75": 100, "92": 103, "93": 100, "94": 100,
    "33": 100, "34": 104, "13": 100, "06": 100,
    "40": 100, "83": 100, "30": 104,
    "2A": 100, "2B": 100
}

colors_scale = [
    "#6b3a1f", "#a0672a", "#c8a96e", "#e8d9b5",
    "#f5f0e8", "#c8e8d8", "#8dd0c0", "#4db8a8",
    "#00897b"
]

index_vals = [65, 75, 85, 95, 100, 105, 115, 125, 135]

colormap = cm.LinearColormap(
    colors=colors_scale,
    vmin=65,
    vmax=135,
    index=index_vals,
    caption="Exposition (%)"
)

# ==============================================================================
# 4. CARTE FOLIUM
# ==============================================================================
m = folium.Map(
    location=[46.6, 2.5],
    zoom_start=6,
    tiles="cartodbpositron",
    prefer_canvas=True
)

Fullscreen(
    position="topleft",
    title="Plein écran",
    title_cancel="Quitter",
    force_separate_button=True
).add_to(m)

# ==============================================================================
# 5. STYLE DÉPARTEMENTS
# ==============================================================================
def style_dept(feature):
    code = feature["properties"].get("code", "")
    value = departement_values.get(code, 100)

    return {
        "fillColor": colormap(value),
        "fillOpacity": 0.85,
        "color": "none",
        "weight": 0
    }

folium.GeoJson(
    departements_geojson,
    name="Départements",
    style_function=style_dept,
    interactive=False
).add_to(m)

# ==============================================================================
# 6. EPCI (simple + stable)
# ==============================================================================
def style_epci(feature):
    return {
        "fillOpacity": 0,
        "color": "#111111",
        "weight": 0.6
    }

def highlight_epci(feature):
    return {
        "color": "#FF0000",
        "weight": 2
    }

folium.GeoJson(
    epci_geojson,
    name="EPCI",
    style_function=style_epci,
    highlight_function=highlight_epci,
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "siren"],
        aliases=["Intercommunalité :", "SIREN :"]
    )
).add_to(m)

# ==============================================================================
# 7. LÉGENDE
# ==============================================================================
colormap.add_to(m)

title_html = """
<div style="
position: fixed;
top: 15px;
left: 60px;
z-index:9999;
background:white;
padding:10px;
border-radius:6px;
box-shadow:0 2px 8px rgba(0,0,0,0.2);
font-size:12px;
">
<b>Risque de ruissellement</b><br>
Exposition départementale (%)
</div>
"""

m.get_root().html.add_child(folium.Element(title_html))

# ==============================================================================
# 8. AFFICHAGE STREAMLIT
# ==============================================================================
st_folium(m, width=None, height=800)
