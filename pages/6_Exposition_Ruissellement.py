import os
import folium
from folium.plugins import Fullscreen
import geopandas as gpd
import streamlit as st  # <-- AJOUTÉ POUR STREAMLIT
from streamlit_folium import st_folium  # <-- AJOUTÉ POUR STREAMLIT

# Configuration de la page web Streamlit (Prend tout l'écran)
st.set_page_config(layout="wide")

# ==============================================================================
# 1. CHARGEMENT ET SIMPLIFICATION DES DONNÉES
# ==============================================================================
# Couche Départements
chemin_dept = "departements.geojson"
gdf_dept = gpd.read_file(chemin_dept)
if gdf_dept.crs is not None:
    gdf_dept = gdf_dept.to_crs(epsg=4326)

# Couche EPCI
chemin_epci = "epci-100m.geojson"
gdf_epci = gpd.read_file(chemin_epci)
if gdf_epci.crs is not None:
    gdf_epci = gdf_epci.to_crs(epsg=4326)

# Sécurité anti-page blanche : Simplification des géométries
gdf_epci["geometry"] = gdf_epci["geometry"].simplify(tolerance=0.008, preserve_topology=True)

# Détection automatique des colonnes pour les Départements
colonne_trouvee = "nom"
for pour_chercher in ['nom', 'NOM', 'nom_dept', 'NOM_DEPT', 'Nom']:
    if pour_chercher in gdf_dept.columns:
        colonne_trouvee = pour_chercher
        break

# Détection automatique des colonnes pour les EPCI
colonne_code_epci = "siren" if "siren" in gdf_epci.columns else ("code" if "code" in gdf_epci.columns else "CODE")
colonne_nom_epci = "nom" if "nom" in gdf_epci.columns else ("NOM" if "NOM" in gdf_epci.columns else "NOM_EPCI")

# ==============================================================================
# 2. INITIALISATION DE LA CARTE
# ==============================================================================
m = folium.Map(tiles="OpenStreetMap", prefer_canvas=True)

Fullscreen(
    position="topleft",
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True
).add_to(m)

# ==============================================================================
# 3. STYLE DES DÉPARTEMENTS (VOS COULEURS EXACTES, ZÉRO CONTOUR)
# ==============================================================================
def determiner_style_dept(feature):
    nom_actuel = str(feature['properties'].get(colonne_trouvee, ''))
    code_actuel = str(feature['properties'].get('code', ''))
    
    # --- VIOLET (> 15%) ---
    if (
        "Landes" in nom_actuel or code_actuel == "40" or
        "Var" in nom_actuel or code_actuel == "83" or
        "Gard" in nom_actuel or code_actuel == "30" or
        "Hérault" in nom_actuel or code_actuel == "34" or
        "Gironde" in nom_actuel or code_actuel == "33" or
        "Nord" in nom_actuel or code_actuel == "59" or
        "Hauts-de-Seine" in nom_actuel or code_actuel == "92" or
        "Val-de-Marne" in nom_actuel or code_actuel == "94" or
        "Bouches-du-Rhône" in nom_actuel or code_actuel == "13" or
        "Seine-Saint-Denis" in nom_actuel or code_actuel == "93" or
        "Paris" in nom_actuel or code_actuel == "75" or
        "Haute-Corse" in nom_actuel or code_actuel in ["2B", "2b"]
    ):
        couleur = "#4B0082"  # --- ROSE FUCHSIA (12 - 15%) ---
    elif (
        "Seine-Maritime" in nom_actuel or code_actuel == "76" or
        "Eure" in nom_actuel or code_actuel == "27" or
        "Somme" in nom_actuel or code_actuel == "80" or
        "Pyrénées-Orientales" in nom_actuel or code_actuel == "66" or
        "Aude" in nom_actuel or code_actuel == "11" or
        "Doubs" in nom_actuel or code_actuel == "25" or
        "Jura" in nom_actuel or code_actuel == "39" or
        "Yvelines" in nom_actuel or code_actuel == "78" or
        "Essonne" in nom_actuel or code_actuel == "91" or
        "Vaucluse" in nom_actuel or code_actuel == "84" or
        "Puy-de-Dôme" in nom_actuel or code_actuel == "63" or
        "Côte-d'Or" in nom_actuel or code_actuel == "21" or
        "Ain" in nom_actuel or code_actuel == "01" or
        "Drôme" in nom_actuel or code_actuel == "26" or
        "Isère" in nom_actuel or code_actuel == "38" or
        "Corse-du-Sud" in nom_actuel or code_actuel in ["2A", "2a"]
    ):
        couleur = "#FF1493"  # --- ROSE NORMAL (9 - 12%) ---
    elif (
        "Hautes-Pyrénées" in nom_actuel or code_actuel == "65" or
        "Loire-Atlantique" in nom_actuel or code_actuel == "44" or
        "Vendée" in nom_actuel or code_actuel == "85" or
        "Pas-de-Calais" in nom_actuel or code_actuel == "62" or
        "Charente-Maritime" in nom_actuel or code_actuel == "17" or
        "Alpes-Maritimes" in nom_actuel or code_actuel == "06" or
        "Savoie" in nom_actuel or code_actuel == "73" or
        "Aisne" in nom_actuel or code_actuel == "02" or
        "Loiret" in nom_actuel or code_actuel == "45" or
        "Oise" in nom_actuel or code_actuel == "60" or
        "Deux-Sèvres" in nom_actuel or code_actuel == "79" or
        "Charente" in nom_actuel or code_actuel == "16" or
        "Lot" in nom_actuel or code_actuel == "46" or
        "Aube" in nom_actuel or code_actuel == "10" or
        "Indre" in nom_actuel or code_actuel == "36" or
        "Hautes-Alpes" in nom_actuel or code_actuel == "05" or
        "Lozère" in nom_actuel or code_actuel == "48" or
        "Ardèche" in nom_actuel or code_actuel == "07" or
        "Cher" in nom_actuel or code_actuel == "18" or
        "Haute-Loire" in nom_actuel or code_actuel == "43"
    ):
        couleur = "#FF69B4"
         
    # --- ROSE CLAIR (6 - 9%) ---
    elif (
        "Gers" in nom_actuel or code_actuel == "32" or
        "Pyrénées-Atlantiques" in nom_actuel or code_actuel == "64" or
        "Dordogne" in nom_actuel or code_actuel == "24" or
        "Finistère" in nom_actuel or code_actuel == "29" or
        "Côtes-d'Armor" in nom_actuel or code_actuel == "22" or
        "Morbihan" in nom_actuel or code_actuel == "56" or
        "Ille-et-Vilaine" in nom_actuel or code_actuel == "35" or
        "Lot-et-Garonne" in nom_actuel or code_actuel == "47" or
        "Calvados" in nom_actuel or code_actuel == "14" or
        "Orne" in nom_actuel or code_actuel == "61" or
        "Haute-Vienne" in nom_actuel or code_actuel == "87" or
        "Creuse" in nom_actuel or code_actuel == "23" or
        "Corrèze" in nom_actuel or code_actuel == "19" or
        "Manche" in nom_actuel or code_actuel == "50" or
        "Marne" in nom_actuel or code_actuel == "51" or
        "Ariège" in nom_actuel or code_actuel == "09" or
        "Haute-Garonne" in nom_actuel or code_actuel == "31" or
        "Yonne" in nom_actuel or code_actuel == "89" or
        "Loir-et-Cher" in nom_actuel or code_actuel == "41" or
        "Tarn" in nom_actuel or code_actuel == "81" or
        "Aveyron" in nom_actuel or code_actuel == "12" or
        "Cantal" in nom_actuel or code_actuel == "15" or
        "Mayenne" in nom_actuel or code_actuel == "53" or
        "Sarthe" in nom_actuel or code_actuel == "72" or
        "Maine-et-Loire" in nom_actuel or code_actuel == "49" or
        "Haute-Saône" in nom_actuel or code_actuel == "70" or
        "Haut-Rhin" in nom_actuel or code_actuel == "68" or
        "Allier" in nom_actuel or code_actuel == "03" or
        "Nièvre" in nom_actuel or code_actuel == "58" or
        "Vienne" in nom_actuel or code_actuel == "86" or
        "Indre-et-Loire" in nom_actuel or code_actuel == "37" or
        "Alpes-de-Haute-Provence" in nom_actuel or code_actuel == "04" or
        "Saône-et-Loire" in nom_actuel or code_actuel == "71" or
        "Rhône" in nom_actuel or code_actuel == "69" or
        "Loire" in nom_actuel or code_actuel == "42"
    ):
        couleur = "#FFB6C1"  # --- BEIGE ROSÉ (0%) ---
    elif (
        "Bas-Rhin" in nom_actuel or code_actuel == "67" or
        "Moselle" in nom_actuel or code_actuel == "57" or
        "Ardennes" in nom_actuel or code_actuel == "08" or
        "Vosges" in nom_actuel or code_actuel == "88" or
        "Meuse" in nom_actuel or code_actuel == "55"
    ):
        couleur = "#FFF5EE"
    else:
        couleur = "#f8f9fa"

    return {
        "fillColor": couleur,
        "fillOpacity": 0.85 if couleur != "#f8f9fa" else 0.4,
        "weight": 0,
        "color": "none"
    }

folium.GeoJson(
    gdf_dept,
    name="Couleurs Départements (Fond)",
    style_function=determiner_style_dept,
    interactive=False
).add_to(m)

# ==============================================================================
# 4. COUCHE EPCI (CONTOURS BLANCS, SURVOL ET CLIC ROUGE)
# ==============================================================================
def style_base_epci(feature):
    return {
        "fillColor": "rgba(0,0,0,0)",
        "fillOpacity": 0,
        "color": "#FFFFFF",
        "weight": 1.0
    }

def style_highlight_epci(feature):
    return {
        "color": "#FF0000",
        "weight": 2.5
    }

folium.GeoJson(
    gdf_epci,
    name="Contours EPCI",
    style_function=style_base_epci,
    highlight_function=style_highlight_epci,
    tooltip=folium.GeoJsonTooltip(
        fields=[colonne_nom_epci, colonne_code_epci],
        aliases=["Intercommunalité :", "Code SIREN :"],
        localize=True,
        sticky=True
    ),
    popup=folium.GeoJsonPopup(
        fields=[colonne_nom_epci, colonne_code_epci],
        aliases=["Nom EPCI :", "Numéro SIREN :"],
        localize=True
    )
).add_to(m)

# ==============================================================================
# 5. TITRE PRINCIPAL ET LÉGENDE DE LA CARTE (HTML / CSS NAtif)
# ==============================================================================
html_titre_et_legende = """
<div style="
    position: fixed; 
    top: 20px; right: 20px; width: 320px; height: auto; 
    z-index:9999; font-family: Arial, sans-serif; font-size:13px;
    background-color: white; padding: 15px; border-radius: 8px; 
    box-shadow: 0 0 15px rgba(0,0,0,0.2); line-height: 1.5;
">
    <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; color: #333;">
        Exposition au Risque de Ruissellement 
    </div>
    <div style="font-size: 11px; color: #666; margin-bottom: 15px; border-bottom: 1px solid #ddd; padding-bottom: 8px;">
        Part communale moyenne extrapolée par département et maillage des intercommunalités (EPCI).
    </div>
    
    <div style="font-weight: bold; margin-bottom: 8px; color: #444;">Légende :</div>
    
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="width: 20px; height: 15px; background-color: #4B0082; border: 1px solid #310054; margin-right: 10px; border-radius: 2px;"></div>
        <span>Supérieur à 15 %</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="width: 20px; height: 15px; background-color: #FF1493; border: 1px solid #C71585; margin-right: 10px; border-radius: 2px;"></div>
        <span>Entre 12 et 15 %</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="width: 20px; height: 15px; background-color: #FF69B4; border: 1px solid #C71585; margin-right: 10px; border-radius: 2px;"></div>
        <span>Entre 9 et 12 %</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="width: 20px; height: 15px; background-color: #FFB6C1; border: 1px solid #FF91A4; margin-right: 10px; border-radius: 2px;"></div>
        <span>Entre 6 et 9 %</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <div style="width: 20px; height: 15px; background-color: #FFF5EE; border: 1px solid #E6D7CE; margin-right: 10px; border-radius: 2px;"></div>
        <span>0 %</span>
    </div>
    <div style="display: flex; align-items: center; margin-top: 10px; padding-top: 5px; border-top: 1px dashed #eee;">
        <div style="width: 20px; height: 2px; background-color: #FFFFFF; border: 1px solid #bbb; margin-right: 10px;"></div>
        <span style="font-size: 11px; color: #555;">Contours Blancs : Limites des EPCI</span>
    </div>
</div>
"""
# Injection du bloc HTML dans la structure de la carte Folium
m.get_root().html.add_child(folium.Element(html_titre_et_legende))

# Cadrage
m.fit_bounds(gdf_epci.total_bounds.tolist())

# ==============================================================================
# 6. RENDU WEB VIA STREAMLIT
# ==============================================================================
st_folium(m, width="100%", height=750)
