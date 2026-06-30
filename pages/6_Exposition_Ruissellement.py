import folium
from folium.plugins import Fullscreen
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

# Configuration de la page Streamlit (Largeur maximale)
st.set_page_config(layout="wide", page_title="Carte Ruissellement")

# ==============================================================================
# 1. CONFIGURATION DES SOURCES GITHUB (À AJUSTER)
# ==============================================================================
# IMPORTANT : Remplacez par vos propres URLs "Raw" de GitHub si nécessaire.
# Pour obtenir l'URL Raw : Allez sur votre fichier sur GitHub, cliquez sur "Raw" et copiez l'adresse.

@st.cache_data # Permet de mettre en cache pour éviter de recharger à chaque clic
def charger_donnees():
    # Exemple si vos fichiers sont à la racine de votre dépôt GitHub :
    url_dept = "departements.geojson" 
    url_epci = "epci-100m.geojson"
    
    # Lecture des fichiers (Geopandas accepte directement les URLs ou chemins locaux)
    gdf_d = gpd.read_file(url_dept)
    if gdf_d.crs is not None:
        gdf_d = gdf_d.to_crs(epsg=4326)
        
    gdf_e = gpd.read_file(url_epci)
    if gdf_e.crs is not None:
        gdf_e = gdf_e.to_crs(epsg=4326)
        
    # Sécurité anti-plantage : Simplification des contours
    gdf_e["geometry"] = gdf_e["geometry"].simplify(tolerance=0.008, preserve_topology=True)
    
    return gdf_d, gdf_e

# Chargement effectif
gdf_dept, gdf_epci = charger_donnees()

# --- Détection des colonnes ---
colonne_trouvee = "nom"
for pour_chercher in ['nom', 'NOM', 'nom_dept', 'NOM_DEPT', 'Nom']:
    if pour_chercher in gdf_dept.columns:
        colonne_trouvee = pour_chercher
        break

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
# 3. STYLE DES DÉPARTEMENTS
# ==============================================================================
def determiner_style_dept(feature):
    nom_actuel = str(feature['properties'].get(colonne_trouvee, ''))
    code_actuel = str(feature['properties'].get('code', ''))
    
    if (
        "Landes" in nom_actuel or code_actuel == "40" or "Var" in nom_actuel or code_actuel == "83" or
        "Gard" in nom_actuel or code_actuel == "30" or "Hérault" in nom_actuel or code_actuel == "34" or
        "Gironde" in nom_actuel or code_actuel == "33" or "Nord" in nom_actuel or code_actuel == "59" or
        "Hauts-de-Seine" in nom_actuel or code_actuel == "92" or "Val-de-Marne" in nom_actuel or code_actuel == "94" or
        "Bouches-du-Rhône" in nom_actuel or code_actuel == "13" or "Seine-Saint-Denis" in nom_actuel or code_actuel == "93" or
        "Paris" in nom_actuel or code_actuel == "75" or "Haute-Corse" in nom_actuel or code_actuel in ["2B", "2b"]
    ):
        couleur = "#4B0082"
    elif (
        "Seine-Maritime" in nom_actuel or code_actuel == "76" or "Eure" in nom_actuel or code_actuel == "27" or
        "Somme" in nom_actuel or code_actuel == "80" or "Pyrénées-Orientales" in nom_actuel or code_actuel == "66" or
        "Aude" in nom_actuel or code_actuel == "11" or "Doubs" in nom_actuel or code_actuel == "25" or
        "Jura" in nom_actuel or code_actuel == "39" or "Yvelines" in nom_actuel or code_actuel == "78" or
        "Essonne" in nom_actuel or code_actuel == "91" or "Vaucluse" in nom_actuel or code_actuel == "84" or
        "Puy-de-Dôme" in nom_actuel or code_actuel == "63" or "Côte-d'Or" in nom_actuel or code_actuel == "21" or
        "Ain" in nom_actuel or code_actuel == "01" or "Drôme" in nom_actuel or code_actuel == "26" or
        "Isère" in nom_actuel or code_actuel == "38" or "Corse-du-Sud" in nom_actuel or code_actuel in ["2A", "2a"]
    ):
        couleur = "#FF1493"
    elif (
        "Hautes-Pyrénées" in nom_actuel or code_actuel == "65" or "Loire-Atlantique" in nom_actuel or code_actuel == "44" or
        "Vendée" in nom_actuel or code_actuel == "85" or "Pas-de-Calais" in nom_actuel or code_actuel == "62" or
        "Charente-Maritime" in nom_actuel or code_actuel == "17" or "Alpes-Maritimes" in nom_actuel or code_actuel == "06" or
        "Savoie" in nom_actuel or code_actuel == "73" or "Aisne" in nom_actuel or code_actuel == "02" or
        "Loiret" in nom_actuel or code_actuel == "45" or "Oise" in nom_actuel or code_actuel == "60" or
        "Deux-Sèvres" in nom_actuel or code_actuel == "79" or "Charente" in nom_actuel or code_actuel == "16" or
        "Lot" in nom_actuel or code_actuel == "46" or "Aube" in nom_actuel or code_actuel == "10" or
        "Indre" in nom_actuel or code_actuel == "36" or "Hautes-Alpes" in nom_actuel or code_actuel == "05" or
        "Lozère" in nom_actuel or code_actuel == "48" or "Ardèche" in nom_actuel or code_actuel == "07" or
        "Cher" in nom_actuel or code_actuel == "18" or "Haute-Loire" in nom_actuel or code_actuel == "43"
    ):
        couleur = "#FF69B4"
    elif (
        "Gers" in nom_actuel or code_actuel == "32" or "Pyrénées-Atlantiques" in nom_actuel or code_actuel == "64" or
        "Dordogne" in nom_actuel or code_actuel == "24" or "Finistère" in nom_actuel or code_actuel == "29" or
        "Côtes-d'Armor" in nom_actuel or code_actuel == "22" or "Morbihan" in nom_actuel or code_actuel == "56" or
        "Ille-et-Vilaine" in nom_actuel or code_actuel == "35" or "Lot-et-Garonne" in nom_actuel or code_actuel == "47" or
        "Calvados" in nom_actuel or code_actuel == "14" or "Orne" in nom_actuel or code_actuel == "61" or
        "Haute-Vienne" in nom_actuel or code_actuel == "87" or "Creuse" in nom_actuel or code_actuel == "23" or
        "Corrèze" in nom_actuel or code_actuel == "19" or "Manche" in nom_actuel or code_actuel == "50" or
        "Marne" in nom_actuel or code_actuel == "51" or "Ariège" in nom_actuel or code_actuel == "09" or
        "Haute-Garonne" in nom_actuel or code_actuel == "31" or "Yonne" in nom_actuel or code_actuel == "89" or
        "Loir-et-Cher" in nom_actuel or code_actuel == "41" or "Tarn" in nom_actuel or code_actuel == "81" or
        "Aveyron" in nom_actuel or code_actuel == "12" or "Cantal" in nom_actuel or code_actuel == "15" or
        "Mayenne" in nom_actuel or code_actuel == "53" or "Sarthe" in nom_actuel or code_actuel == "72" or
        "Maine-et-Loire" in nom_actuel or code_actuel == "49" or "Haute-Saône" in nom_actuel or code_actuel == "70" or
        "Haut-Rhin" in nom_actuel or code_actuel == "68" or "Allier" in nom_actuel or code_actuel == "03" or
        "Nièvre" in nom_actuel or code_actuel == "58" or "Vienne" in nom_actuel or code_actuel == "86" or
        "Indre-et-Loire" in nom_actuel or code_actuel == "37" or "Alpes-de-Haute-Provence" in nom_actuel or code_actuel == "04" or
        "Saône-et-Loire" in nom_actuel or code_actuel == "71" or "Rhône" in nom_actuel or code_actuel == "69" or
        "Loire" in nom_actuel or code_actuel == "42"
    ):
        couleur = "#FFB6C1"
    elif (
        "Bas-Rhin" in nom_actuel or code_actuel == "67" or "Moselle" in nom_actuel or code_actuel == "57" or
        "Ardennes" in nom_actuel or code_actuel == "08" or "Vosges" in nom_actuel or code_actuel == "88" or
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
# 4. COUCHE EPCI
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
# 5. TITRE PRINCIPAL ET LÉGENDE (ADAPTÉ POUR STREAMLIT AVEC LE CÔTÉ DROIT DROIT)
# ==============================================================================
html_titre_et_legende = """
<div style="
    position: fixed; 
    top: 20px; right: 20px; width: 280px; height: auto; 
    z-index:9999; font-family: Arial, sans-serif; font-size:12px;
    background-color: white; padding: 12px; border-radius: 8px; 
    box-shadow: 0 0 15px rgba(0,0,0,0.2); line-height: 1.4;
">
    <div style="font-weight: bold; font-size: 13px; margin-bottom: 5px; color: #333;">
        Exposition au Ruissellement 
    </div>
    <div style="font-size: 10px; color: #666; margin-bottom: 10px; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
        Part communale moyenne extrapolée par département et limites des EPCI.
    </div>
    
    <div style="font-weight: bold; margin-bottom: 5px; color: #444;">Légende :</div>
    <div style="display: flex; align-items: center; margin-bottom: 4px;"><div style="width: 18px; height: 12px; background-color: #4B0082; margin-right: 8px; border-radius: 2px;"></div><span>Supérieur à 15 %</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 4px;"><div style="width: 18px; height: 12px; background-color: #FF1493; margin-right: 8px; border-radius: 2px;"></div><span>Entre 12 et 15 %</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 4px;"><div style="width: 18px; height: 12px; background-color: #FF69B4; margin-right: 8px; border-radius: 2px;"></div><span>Entre 9 et 12 %</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 4px;"><div style="width: 18px; height: 12px; background-color: #FFB6C1; margin-right: 8px; border-radius: 2px;"></div><span>Entre 6 et 9 %</span></div>
    <div style="display: flex; align-items: center; margin-bottom: 4px;"><div style="width: 18px; height: 12px; background-color: #FFF5EE; border: 1px solid #ddd; margin-right: 8px; border-radius: 2px;"></div><span>0 %</span></div>
    <div style="display: flex; align-items: center; margin-top: 8px; padding-top: 4px; border-top: 1px dashed #eee;">
        <div style="width: 18px; height: 2px; background-color: #FFFFFF; border: 1px solid #aaa; margin-right: 8px;"></div>
        <span style="font-size: 10px; color: #555;">Contours Blancs : EPCI</span>
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(html_titre_et_legende))

m.fit_bounds(gdf_epci.total_bounds.tolist())

# ==============================================================================
# 6. RENDU STREAMLIT (L'ÉQUIVALENT DU "m" DE FIN)
# ==============================================================================
# Affiche la carte folium de manière fluide et dynamique dans l'application web
st_folium(m, width="100%", height=700, returned_objects=[])
