import json
import folium
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen, Search  # Import de Search ici
from streamlit_folium import st_folium

# Le titre de votre page Streamlit
st.title("Zonage Inondation par EPCI (Établissement Public de Coopération Intercommunale)")
#  SOUS-TITRE AVEC VOTRE PHRASE MÉTHODOLOGIQUE COMPLÈTE
st.markdown(
    """
    <div style="
        font-size:13px;
        color:#666;
        margin-bottom:20px;
        line-height:1.5;
        text-align: justify;
    ">
    Données :</strong> Données internes Groupama. Le zonage inondation est initialement défini à la maille IRIS. 
    Afin de refléter une approche prudente du risque, la valeur maximale a été successivement conservée à la maille communale, 
    puis à la maille EPCI. Ainsi, il suffit qu'une seule IRIS soit classée en risque maximal (3 - Rouge) pour que l'ensemble de son EPCI 
    apparaisse en rouge sur la carte.<br>
    </div>
    """,
    unsafe_allow_html=True,
)

# 1. Chargement des données avec mise en cache (Correction Encodage Latin1)
@st.cache_data
def load_data():
    df = pd.read_csv(
        "BASE_IRIS.csv",
        sep=";",
        encoding="latin1",
        dtype={"epci_code": str},
    )
    df["ZONIER INONDATION"] = df["ZONIER INONDATION"].astype(int)
    return df

@st.cache_data
def load_geojson():
    with open("epci-100m.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

# Chargement effectif des fichiers
df_epci = load_data()
geojson_epci = load_geojson()

# 2. Créer la carte Folium centrée sur la France
m = folium.Map(
    location=[46.603354, 1.888334], zoom_start=6, tiles="OpenStreetMap"
)

# Option Plein Écran
Fullscreen(
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True,
).add_to(m)

# 3. Définir la fonction de couleur (1 -> Vert, 2 -> Orange, 3 -> Rouge)
couleurs_dict = {
    row["epci_code"]: (
        "#2ecc71"
        if row["ZONIER INONDATION"] == 1
        else "#e67e22" if row["ZONIER INONDATION"] == 2 else "#e74c3c"
    )
    for _, row in df_epci.iterrows()
}

def style_function(feature):
    code_geojson = feature["properties"].get("code")
    couleur = couleurs_dict.get(code_geojson, "#bdc3c7")

    return {
        "fillColor": couleur,
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.7,
    }

def highlight_function(feature):
    return {
        "weight": 3,
        "color": "black",
        "fillOpacity": 0.9,
    }

# 4. Créer un calque et ajouter les contours GeoJSON avec survol et recherche
layer_epci = folium.FeatureGroup(name="EPCI").add_to(m)

geo = folium.GeoJson(
    geojson_epci,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["code", "nom"],
        aliases=["Code EPCI: ", "Nom EPCI: "],
        style=(
            "background-color: white; color: #333333; font-family: sans-serif; font-size: 13px; padding: 10px;"
        ),
    ),
).add_to(layer_epci)

# Intégration de la barre de recherche
Search(
    layer=layer_epci,
    geom_type="Polygon",
    search_label="nom",
    placeholder="🔎 Rechercher un EPCI (entrez le nom)",
    collapsed=False
).add_to(m)

# 5. Ajouter la légende HTML directement avec le titre en GRAS
html_legende = """
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 200px; height: 130px; 
    z-index:9999; 
    background-color: white;
    padding: 12px;
    border: 2px solid grey;
    border-radius: 5px;
    font-family: sans-serif;
    font-size: 14px;
    opacity: 0.9;
">
    <strong style="font-size: 15px; font-weight: bold; display: block; margin-bottom: 8px;">Zonage Inondation EPCI</strong>
    <i style="background: #2ecc71; width: 18px; height: 18px; float: left; margin-right: 8px; opacity: 0.7;"></i> 1 - Zone Verte<br>
    <i style="background: #e67e22; width: 18px; height: 18px; float: left; margin-right: 8px; opacity: 0.7;"></i> 2 - Zone Orange<br>
    <i style="background: #e74c3c; width: 18px; height: 18px; float: left; margin-right: 8px; opacity: 0.7;"></i> 3 - Zone Rouge<br>
</div>
"""
m.get_root().html.add_child(folium.Element(html_legende))

# 6. Afficher la carte dans votre page Streamlit
st_folium(m, use_container_width=True, height=700)
