
import json
import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen
from shapely.geometry import shape
from streamlit_folium import st_folium

# Configuration de la page
st.set_page_config(layout="wide")
st.title("Carte interactive des arrêtés CatNat par Intercommunalité")
st.subheader("Période 2000-2026 | Péril : Inondations et Coulées de Boue")

# =========================================================================
# 1. CHARGEMENT DU CSV (Depuis la racine du dépôt GitHub)
# =========================================================================


@st.cache_data
def load_csv():
    # Cherche le fichier directement à la racine du dépôt GitHub
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

    df = pd.DataFrame(
        data_lines, columns=["epci_code", "epci_nom", "Nombre_Arretes"]
    )
    df["epci_code"] = df["epci_code"].astype(str)
    return df


with st.spinner("Analyse du fichier de données CatNat..."):
    df_epci_counts = load_csv()

# =========================================================================
# 2. LECTURE DES CONTOURS GÉOMÉTRIQUES (Depuis la racine du dépôt GitHub)
# =========================================================================


@st.cache_data
def load_geojson():
    # Cherche le GeoJSON à la racine du dépôt GitHub
    chemin_geojson = "epci-100m.geojson"
    with open(chemin_geojson, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data["features"]
    rows = []
    for feat in features:
        code_zone = str(feat["properties"]["code"]).strip()
        rows.append(
            {
                "siren_geojson": code_zone,
                "nom": feat["properties"]["nom"],
                "geometry": shape(feat["geometry"]),
            }
        )
    return gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")


with st.spinner("Génération des fonds géographiques..."):
    gdf = load_geojson()

# =========================================================================
# 3. FUSION EXACTE
# =========================================================================
gdf_final = gdf.merge(
    df_epci_counts, left_on="siren_geojson", right_on="epci_code", how="left"
)
gdf_final["Nombre_Arretes"] = gdf_final["Nombre_Arretes"].fillna(0).astype(int)
vrai_max = int(gdf_final["Nombre_Arretes"].max()) if len(gdf_final) > 0 else 100

# =========================================================================
# 4. CONFIGURATION DE LA PALETTE EN DÉGRADÉ CONTINU
# =========================================================================
seuils_visuels = [0, 1, 30, 100, vrai_max]
couleurs_degrade = ["#ffffff", "#e0f3f8", "#74add1", "#313695", "#02023a"]

colormap = cm.LinearColormap(
    colors=couleurs_degrade,
    index=seuils_visuels,
    vmin=0,
    vmax=vmax if "vmax" in locals() else vrai_max,
    caption="Intensité progressive du nombre d'arrêtés CatNat par EPCI",
)


def style_function(feature):
    valeur = feature["properties"]["Nombre_Arretes"]
    couleur = colormap(valeur)
    return {
        "fillColor": couleur,
        "fillOpacity": 0.85 if valeur > 0 else 0.1,
        "color": "#555555",
        "weight": 0.4,
    }


def highlight_function(feature):
    return {"fillOpacity": 0.7, "color": "#ff3333", "weight": 2.5}


# =========================================================================
# 5. CRÉATION DE LA CARTE INTERACTIVE FOLIUM
# =========================================================================
xmin, ymin, xmax, ymax = gdf_final.total_bounds
m = folium.Map(tiles="CartoDB positron", zoom_control=True)
m.fit_bounds([[ymin, xmin], [ymax, xmax]])

Fullscreen(
    position="topright",
    title="Plein écran",
    title_cancel="Quitter",
    force_separate_button=True,
).add_to(m)

tooltip = folium.GeoJsonTooltip(
    fields=["nom", "siren_geojson", "Nombre_Arretes"],
    aliases=["Nom de l'EPCI :", "Code SIREN :", "Nombre d'arrêtés CatNat :"],
    sticky=True,
)

folium.GeoJson(
    gdf_final,
    name="Données EPCI",
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=tooltip,
).add_to(m)

colormap.add_to(m)

titre_html = f"""
             <div style="position: fixed; 
                         top: 15px; left: 70px; width: 460px; height: 55px; 
                         z-index:9999; font-size:14px; background-color: white;
                         border:2px solid #313695; padding: 8px; border-radius: 6px; font-family: sans-serif;">
             <b>Nombre d'arrêtés CatNat par Intercommunalité (EPCI) pour la période 2000-2026</b><br>
             <span style="font-size:11px; color:#555;">Péril : Inondations et Coulées de Boue</span>
             </div>
             """
m.get_root().html.add_child(folium.Element(titre_html))

# =========================================================================
# 6. RENDU DE LA CARTE DANS STREAMLIT
# =========================================================================
st_folium(m, width=1100, height=650, returned_objects=[])
