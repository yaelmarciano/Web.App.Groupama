import folium
import geopandas as gpd
import streamlit as st
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

# ==============================================================================
# 1. CHARGEMENT DONNÉES
# ==============================================================================

gdf_dept = gpd.read_file("departements.geojson")
gdf_epci = gpd.read_file("epci-100m.geojson")

if gdf_dept.crs:
    gdf_dept = gdf_dept.to_crs(4326)

if gdf_epci.crs:
    gdf_epci = gdf_epci.to_crs(4326)

gdf_epci["geometry"] = gdf_epci["geometry"].simplify(
    tolerance=0.008,
    preserve_topology=True
)

# ==============================================================================
# 2. COLONNES
# ==============================================================================

colonne_trouvee = "nom"
for c in ["nom", "NOM", "nom_dept", "NOM_DEPT", "Nom"]:
    if c in gdf_dept.columns:
        colonne_trouvee = c
        break

col_nom_epci = "nom" if "nom" in gdf_epci.columns else "NOM"
col_code_epci = "siren" if "siren" in gdf_epci.columns else "code"

# ==============================================================================
# 3. STREAMLIT
# ==============================================================================

st.set_page_config(layout="wide")
st.title("Exposition au ruissellement")
st.markdown(
    """
<div style="font-size:13px; color:grey; margin-top:-10px; margin-bottom:18px;">
Source : carte de la <b>part de surface communale exposée au risque d'inondation par ruissellement</b> produite par la <b>CCR (Caisse Centrale de Réassurance)</b>. Les couleurs affichées correspondent à la classe majoritaire observée pour chaque département à partir de cette carte, puis les contours des intercommunalités (EPCI) ont été superposés afin de permettre une lecture à cette échelle.
</div>
""",
    unsafe_allow_html=True,
)

m = folium.Map(
    location=[46.6, 2.5],
    zoom_start=6,
    tiles="OpenStreetMap",
    prefer_canvas=True
)

Fullscreen().add_to(m)

# ==============================================================================
# 4. TES COULEURS (INCHANGÉES)
# ==============================================================================

def determiner_style_dept(feature):
    nom_actuel = str(feature['properties'].get(colonne_trouvee, ''))
    code_actuel = str(feature['properties'].get('code', ''))

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
        couleur = "#4B0082"

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
        couleur = "#FF1493"

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
        couleur = "#FFB6C1"

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
        "fillOpacity": 0.85,
        "weight": 0,
        "color": "none"
    }

folium.GeoJson(gdf_dept, style_function=determiner_style_dept).add_to(m)

# ==============================================================================
# 5. EPCI (BLANC + ROUGE SURVOL)
# ==============================================================================

def style_epci(feature):
    return {
        "fillOpacity": 0,
        "color": "#FFFFFF",
        "weight": 1
    }

def highlight_epci(feature):
    return {
        "color": "#FF0000",
        "weight": 3
    }

folium.GeoJson(
    gdf_epci,
    style_function=style_epci,
    highlight_function=highlight_epci,

    tooltip=folium.GeoJsonTooltip(
        fields=[col_nom_epci, col_code_epci],
        sticky=True
    ),

    popup=folium.GeoJsonPopup(
        fields=[col_nom_epci, col_code_epci]
    )
).add_to(m)

# ==============================================================================
# 6. AFFICHAGE
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
        Exposition au risque de ruissellement
    </div>

    <div style="font-size: 11px; color: #666; margin-bottom: 15px; border-bottom: 1px solid #ddd; padding-bottom: 8px;">
        Part de surface communale exposée au risque d'inondation par ruissellement (classe majoritaire par département) avec superposition des contours des intercommunalités (EPCI).
    </div>

    <div style="font-weight: bold; margin-bottom: 8px; color: #444;">
        Légende
    </div>

    <div style="display:flex;align-items:center;margin-bottom:6px;">
        <div style="width:20px;height:15px;background:#4B0082;border:1px solid #310054;margin-right:10px;"></div>
        <span>Supérieur à 15 %</span>
    </div>

    <div style="display:flex;align-items:center;margin-bottom:6px;">
        <div style="width:20px;height:15px;background:#FF1493;border:1px solid #C71585;margin-right:10px;"></div>
        <span>Entre 12 % et 15 %</span>
    </div>

    <div style="display:flex;align-items:center;margin-bottom:6px;">
        <div style="width:20px;height:15px;background:#FF69B4;border:1px solid #C71585;margin-right:10px;"></div>
        <span>Entre 9 % et 12 %</span>
    </div>

    <div style="display:flex;align-items:center;margin-bottom:6px;">
        <div style="width:20px;height:15px;background:#FFB6C1;border:1px solid #FF91A4;margin-right:10px;"></div>
        <span>Entre 6 % et 9 %</span>
    </div>

    <div style="display:flex;align-items:center;margin-bottom:6px;">
        <div style="width:20px;height:15px;background:#FFF5EE;border:1px solid #E6D7CE;margin-right:10px;"></div>
        <span>0 %</span>
    </div>

    <div style="display:flex;align-items:center;margin-top:10px;padding-top:8px;border-top:1px dashed #ddd;">
        <div style="width:20px;height:2px;background:#FFFFFF;border:1px solid #999;margin-right:10px;"></div>
        <span style="font-size:11px;color:#555;">
            Contours blancs : limites des intercommunalités (EPCI)
        </span>
    </div>
</div>
"""

m.get_root().html.add_child(folium.Element(html_titre_et_legende))
st_folium(m, width=1100, height=800)
