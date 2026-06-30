import os
import json
import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

# Configuration de la page Streamlit (Doit être la toute première commande)
st.set_page_config(layout="wide", page_title="Climat - Précipitations")

st.title("Cumul annuel de précipitations")
st.subheader("Rapport à la référence 1976-2005 pour l'horizon lointain")

# ==============================================================================
# 2. CHARGEMENT ET RÉSOLUTION DES CHEMINS DE FICHIERS (Méthode ultra-sécurisée)
# ==============================================================================
repertoire_actuel = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()

chemin_dept = os.path.join(repertoire_actuel, "departements.geojson")
chemin_epci = os.path.join(repertoire_actuel, "epci-100m.geojson")

@st.cache_data
def load_data_climat(path_dept, path_epci):
    # Vérification de sécurité pour le serveur GitHub
    if not os.path.exists(path_dept) or not os.path.exists(path_epci):
        st.error(f"Fichiers introuvables. Vérifiez qu'ils sont bien à la racine de votre GitHub.\nRecherché dans : {repertoire_actuel}")
        st.stop()

    # 1. Chargement direct des Départements via GeoPandas
    gdf_d = gpd.read_file(path_dept)
    if gdf_d.crs is not None:
        gdf_d = gdf_d.to_crs(epsg=4326)

    # 2. Chargement direct des EPCI via GeoPandas
    gdf_e = gpd.read_file(path_epci)
    if gdf_e.crs is not None:
        gdf_e = gdf_e.to_crs(epsg=4326)

    # Détection automatique et nettoyage des colonnes pour les EPCI
    colonne_code = "code" if "code" in gdf_e.columns else ("siren" if "siren" in gdf_e.columns else "CODE")
    colonne_nom = "nom" if "nom" in gdf_e.columns else ("NOM" if "NOM" in gdf_e.columns else "NOM_EPCI")
    gdf_e = gdf_e.rename(columns={colonne_code: "siren", colonne_nom: "nom"})

    # Détection automatique pour les Départements
    colonne_dept = "code"
    for pour_chercher in ["code", "CODE", "code_insee", "dep"]:
        if pour_chercher in gdf_d.columns:
            colonne_dept = pour_chercher
            break
    gdf_d = gdf_d.rename(columns={colonne_dept: "code"})

    # CRUCIAL : Simplification géométrique pour éviter l'écran blanc sur Streamlit Cloud
    gdf_e["geometry"] = gdf_e["geometry"].simplify(tolerance=0.005, preserve_topology=True)

    return gdf_d, gdf_e


with st.spinner("Chargement des fonds cartographiques..."):
    gdf_dept, gdf_epci = load_data_climat(chemin_dept, chemin_epci)

xmin, ymin, xmax, ymax = gdf_epci.total_bounds

# ==============================================================================
# 3. DONNÉES DE COULEURS (PR%) PAR DÉPARTEMENT
# ==============================================================================
departement_values = {
    "59": 104, "62": 104, "02": 104, "08": 104, "57": 104, "67": 104, "68": 104, "54": 104, "55": 104, "88": 104,
    "52": 104, "10": 104, "51": 104, "60": 100, "80": 100, "76": 104, "27": 104, "78": 100, "95": 100, "77": 100,
    "93": 100, "94": 100, "75": 100, "92": 103, "91": 104, "29": 100, "22": 100, "35": 100, "56": 100, "14": 100,
    "50": 100, "61": 100, "28": 104, "45": 100, "41": 100, "37": 100, "36": 100, "18": 100, "23": 100, "03": 100,
    "58": 100, "71": 100, "21": 104, "89": 104, "70": 104, "25": 104, "39": 104, "90": 104, "44": 100, "49": 100,
    "72": 100, "53": 100, "85": 100, "79": 100, "86": 100, "87": 100, "16": 104, "17": 104, "33": 100, "24": 104,
    "19": 100, "15": 100, "43": 100, "63": 100, "47": 100, "40": 100, "64": 100, "32": 100, "82": 100, "46": 104,
    "31": 100, "09": 85,  "65": 88,  "11": 100, "66": 100, "12": 100, "81": 100, "34": 104, "30": 104, "48": 104,
    "13": 100, "83": 100, "06": 100, "84": 100, "04": 100, "05": 100, "26": 100, "07": 104, "69": 104, "42": 100,
    "38": 100, "73": 100, "74": 105, "01": 104, "2A": 100, "2B": 100,
}

colors_scale = ["#6b3a1f", "#a0672a", "#c8a96e", "#e8d9b5", "#f5f0e8", "#c8e8d8", "#8dd0c0", "#4db8a8", "#00897b"]
index_vals = [65, 75, 85, 95, 100, 105, 115, 125, 135]

colormap = cm.LinearColormap(
    colors=colors_scale, vmin=65, vmax=135, index=index_vals, caption="PR [%]"
)

# ==============================================================================
# 4. INITIALISATION DE LA CARTE
# ==============================================================================
m = folium.Map(
    tiles="cartodbpositron",
    prefer_canvas=True, 
)
m.fit_bounds([[ymin, xmin], [ymax, xmax]])

Fullscreen(
    position="topleft",
    title="Plein écran",
    title_cancel="Quitter",
    force_separate_button=True,
).add_to(m)

# ==============================================================================
# 5. CONFIGURATION DES COUCHES GRAPHIQUES
# ==============================================================================

# --- A. Couche Départements ---
def style_departement(feature):
    dep_code = str(feature["properties"].get("code", ""))
    value = departement_values.get(dep_code, 100)
    return {
        "fillColor": colormap(value),
        "fillOpacity": 0.85,
        "color": "none",
        "weight": 0,
    }

folium.GeoJson(
    gdf_dept,
    name="Couleurs Précipitations (Dép)",
    style_function=style_departement,
    interactive=False,
).add_to(m)

# --- B. Couche EPCI ---
def style_epci(feature):
    return {"fillOpacity": 0, "color": "#111111", "weight": 0.5}

def highlight_epci(feature):
    return {"fillOpacity": 0.1, "color": "#FF0000", "weight": 2.0}

tooltip_epci = folium.GeoJsonTooltip(
    fields=["nom", "siren"], 
    aliases=["Intercommunalité :", "Code SIREN :"], 
    sticky=True
)

folium.GeoJson(
    gdf_epci,
    name="Contours EPCI",
    style_function=style_epci,
    highlight_function=highlight_epci,
    tooltip=tooltip_epci,
).add_to(m)

# ==============================================================================
# 6. HABILLAGE ET RENDU FINAL POUR STREAMLIT
# ==============================================================================
colormap.add_to(m)

# Titre flottant injecté sur la carte
title_html = """
<div style="position: fixed; top: 15px; left: 70px; z-index: 9999; background: white; padding: 10px 14px; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.25); font-family: Arial, sans-serif; max-width: 380px;">
    <div style="font-size:12px; font-weight:bold; color:#222;">
        Cumul annuel de précipitations : rapport (%) à référence 1976-2005<br>pour l'horizon lointain (2071-2100)
    </div>
    <div style="font-size:11px; color:#555; margin-top:4px;">
        Scénario d'émissions modérées (RCP4.5) — Découpage EPCI
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))
folium.LayerControl().add_to(m)

# Rendu officiel via streamlit_folium
st_folium(m, width="100%", height=700)
