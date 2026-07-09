import json
import folium
import branca.colormap as cm
from folium.plugins import Fullscreen
import streamlit as st
from streamlit_folium import st_folium


st.set_page_config(layout="wide")

# 1. Charger les deux fichiers geojson
# Note pour GitHub : Assurez-vous que ces fichiers sont bien poussés à la racine ou au même niveau de votre repo
with open("departements.geojson", "r", encoding="utf-8") as f:
    geojson_departements = json.load(f)

with open("epci-100m.geojson", "r", encoding="utf-8") as f:
    geojson_epci = json.load(f)

# 2. Créer la carte centrée sur la France
m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

# 3. Ajouter le bouton Plein Écran
Fullscreen(
    position="topleft",
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True,
).add_to(m)

# 4. Ajout du Titre HTML demandé
titre_html = """
<div style="position: fixed; 
            top: 10px; left: 50px; width: auto; height: auto; 
            background-color: white; border: 2px solid grey; z-index: 9999; 
            padding: 10px; font-size: 14px; font-weight: bold; border-radius: 5px;">
    Cumul hivernal de précipitations : rapport (%) à référence 1976-2005<br>
    Pour l'horizon lointain (2071-2100)<br>
    <span style="font-weight: normal; font-size: 12px; color: #555;">
        Scénario d'émissions modérées (RCP4.5) — Découpage EPCI
    </span>
</div>
"""
m.get_root().html.add_child(folium.Element(titre_html))

# 5. Ajout de la légende (Colormap) demandée
colors_scale = [
    "#6b3a1f",
    "#a0672a",
    "#c8a96e",
    "#e8d9b5",
    "#f5f0e8",
    "#c8e8d8",
    "#8dd0c0",
    "#4db8a8",
    "#00897b",
]
index_vals = [65, 75, 85, 95, 100, 105, 115, 125, 135]

colormap = cm.LinearColormap(
    colors=colors_scale, vmin=65, vmax=135, index=index_vals, caption="PR [%]"
)
colormap.add_to(m)

# 6. Listes pour la logique des couleurs (VOS LISTES EXACTES)
deps_clair = [
    "finistère", "finistere", "côtes-d'armor", "cotes-d'armor", "cote d'armor", "manche", "calvados",
    "morbihan", "ille-et-vilaine", "ille et vilaine", "loire-atlantique", "loire atlantique", "vendée", "vendee",
    "deux-sèvres", "deux sevres", "deux-sevres", "creuse", "haute-vienne", "haute vienne",
    "pyrénées-orientales", "pyrenees-orientales", "pyrenne orientales", "marne", "landes",
    "lot-et-garonne", "lot et garonnes", "lot et garonne", "gers", "lot",
    "tarn-et-garonne", "tarn et garonnes", "tarn et garonne", "tarn", "aveyron", "lozère", "lozere", "loreze",
    "cantal", "corrèze", "correze", "mayenne", "aude", "haute-garonne", "haute garonne", "orne", "eure",
    "ardennes", "ardenne", "haute-savoie", "haute savoie", "haute-loire", "haute loire", "corse-du-sud", "corse du sud",
    "yonne", "allier"
]

deps_moyen = [
    "pas-de-calais", "pas de calais", "nord", "somme", "aisne", "seine-maritime", "seine maritime", "oise",
    "seine-et-marne", "seine et marne", "yvelines", "loiret", "loir-et-cher", "loir et cher", "vienne",
    "bas-rhin", "bas rhin", "moselle", "meurthe-et-moselle", "meurthe et moselle", "vosges", "vosques",
    "charente-maritime", "charente maritime", "charente", "dordogne", "essonne", "paris", "val-de-marne", "val de marne",
    "val-d'oise", "val d'oise", "val doise", "hauts-de-seine", "hauts de seine", "haut sde sein e",
    "seine-saint-denis", "seine saint dinis", "bouches-du-rhône", "bouches du rhone", "var",
    "alpes-de-haute-provence", "alpes de haute provence", "meuse", "haute-saône", "haute saone",
    "hautes-alpes", "hautes alpes", "jura", "doubs", "ain", "indre-et-loire", "indre et loire",
    "eure-et-loir", "eure et loire", "gironde", "girondes", "ardèche", "ardeche", "gard", "sarthe", "srathe",
    "maine-et-loire", "maine et loire", "maine et lore", "côte-d'or", "cote d'or", "cote dor", "haute-marne", "haute marne",
    "isère", "isere", "drôme", "drome", "hérault", "herault", "haute-corse", "haute corse", "haute corsee",
    "aube", "cher", "nièvre", "nievre", "saône-et-loire", "saone et loire", "puy-de-dôme", "puy de dome", "indre"
]

deps_fonce = [
    "territoire de belfort", "territoire-de-belfort", "belfort", "haut-rhin", "haut rhin", "vaucluse",
    "alpes-maritimes", "alpes maritimes", "rhône", "rhone", "loire"
]

deps_blanc = [
    "pyrénées-atlantiques", "pyrenees-atlantiques", "pyrenne atlantique", "hautes-pyrénées", "hautes-pyrenees", "haute pyrennes",
    "ariège", "ariege", "savoie"
]

# VOTRE FONCTION DE STYLE EXACTE
def determiner_style(feature):
    nom_dep = feature['properties'].get('nom', '').lower()
    
    if nom_dep in deps_clair:
        return {
            "fillColor": "#c8e8d8",
            "color": "none",
            "weight": 0,
            "fillOpacity": 0.85
        }
    elif nom_dep in deps_moyen:
        return {
            "fillColor": "#4db8a8",
            "color": "none",
            "weight": 0,
            "fillOpacity": 0.85
        }
    elif nom_dep in deps_fonce:
        return {
            "fillColor": "#00897b",
            "color": "none",
            "weight": 0,
            "fillOpacity": 0.85
        }
    elif nom_dep in deps_blanc:
        return {
            "fillColor": "#ffffff",
            "color": "none",
            "weight": 0,
            "fillOpacity": 1.0
        }
    else:
        return {
            "fillColor": "white",
            "color": "none",
            "weight": 0,
            "fillOpacity": 0.2
        }

# Ajouter le fond départemental
folium.GeoJson(
    geojson_departements,
    name="Couleurs Départements",
    style_function=determiner_style,
    interactive=False
).add_to(m)


# 7. Ajouter les contours EPCI transparents
def style_epci(feature):
    return {
        "fillColor": "white",
        "fillOpacity": 0.0,
        "color": "#666666",   # Ligne grise par défaut pour les EPCI non cliqués
        "weight": 1.0
    }

def survol_epci(feature):
    return {
        "weight": 2.0,
        "color": "#333333"
    }

# Création de la couche EPCI
geo_json_layer = folium.GeoJson(
    geojson_epci,
    name="Contours EPCI",
    style_function=style_epci,
    highlight_function=survol_epci,
    popup_on_click=False,
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "code"],
        aliases=["Nom EPCI : ", "Numéro : "],
        localize=True
    ),
    popup=folium.GeoJsonPopup(
        fields=["nom", "code"],
        aliases=["Nom EPCI : ", "Numéro : "],
        localize=True
    )
)

# 8. Script JavaScript
js_clic_epci = """
function(e) {
    var layer = e.target;
    
    // 1. Remettre à zéro le style de tous les autres EPCI
    var parent = layer._eventParents;
    for (var id in parent) {
        if (parent[id]._layers) {
            for (var subId in parent[id]._layers) {
                parent[id]._layers[subId].setStyle({
                    'color': '#666666',
                    'weight': 1.0
                });
            }
        }
    }

    // 2. Appliquer la couleur ROUGE sur l'EPCI sélectionné
    layer.setStyle({
        'color': '#FF0000',
        'weight': 4.0
    });
    
    // 3. Ouvrir manuellement le popup lié à cet EPCI
    layer.openPopup();
    
    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
}
"""

geo_json_layer.add_child(folium.Element(f"""
    <script>
        var layer = {geo_json_layer.get_name()};
        layer.on('click', {js_clic_epci});
    </script>
"""))

geo_json_layer.add_to(m)

# 9. AFFICHER LA CARTE DANS STREAMLIT (Modifié pour Streamlit)
# use_container_width=True permet à la carte de prendre toute la largeur disponible
st_folium(m, use_container_width=True, height=700)
