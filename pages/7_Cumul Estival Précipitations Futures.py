import json
import streamlit as st
import folium
import branca.colormap as cm
# Ajout de Search ici
from folium.plugins import Fullscreen, Search 
from streamlit_folium import st_folium

# 1. Charger les fichiers GeoJSON avec cache pour éviter les lenteurs au rechargement
@st.cache_data
def charger_geometries():
    with open("departements.geojson", "r", encoding="utf-8") as f:
        geojson_departements = json.load(f)
    with open("epci-100m.geojson", "r", encoding="utf-8") as f:
        geojson_epci = json.load(f)
    return geojson_departements, geojson_epci

geojson_departements, geojson_epci = charger_geometries()

# 2. Créer la carte centrée sur la France
m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

# 3. Ajouter le bouton Plein Écran
Fullscreen(
    position="topleft",
    title="Passer en plein écran",
    title_cancel="Quitter le plein écran",
    force_separate_button=True,
).add_to(m)

# 4. Ajout du Titre HTML inséré dans la carte
titre_html = """
<div style="position: fixed; 
            top: 10px; left: 50px; width: auto; height: auto; 
            background-color: white; border: 2px solid grey; z-index: 9999; 
            padding: 10px; font-size: 14px; font-weight: bold; border-radius: 5px;">
    Cumuls hivernaux de précipitations : rapport (%) à référence 1976-2005<br>
    Pour l'horizon lointain (2071-2100)<br>
    <span style="font-weight: normal; font-size: 12px; color: #555;">
        Scénario d'émissions modérées (RCP4.5) — Découpage EPCI
    </span>
</div>
"""
m.get_root().html.add_child(folium.Element(titre_html))

# 5. Légende (Colormap)
colors_scale = ["#6b3a1f", "#a0672a", "#c8a96e", "#e8d9b5", "#f5f0e8", "#c8e8d8", "#8dd0c0", "#4db8a8", "#00897b"]
index_vals = [65, 75, 85, 95, 100, 105, 115, 125, 135]
colormap = cm.LinearColormap(
    colors=colors_scale, vmin=65, vmax=135, index=index_vals, caption="PR [%]"
)
colormap.add_to(m)

# 6. Listes de départements par zones de couleur
deps_75_85 = [
    "morbihan", "loire-atlantique", "loire atlantique", "oure talantiqye",
    "finistère", "finistere", "finisetre", "indre-et-loire", "indre et loire", "indree et loir",
    "maine-et-loire", "maine et loire", "ille-et-vilaine", "ille et vilaine", "ile et villaine",
    "sarthe", "mayenne", "moyenne", "haute-vienne", "haute vienne", "creuse", "landes",
    "bouches-du-rhône", "bouches du rhone", "bouches du rhon", "var"
]

deps_85_95 = [
    "pas-de-calais", "pas de calais", "nord", "somme", "aisne", "seine-maritime", "seine maritime", 
    "oise", "val-d'oise", "val d'oise", "val doise", "eure", "manche", "calvados", "eure-et-loir", 
    "eure et loire", "eure et loir", "yvelines", "seine-saint-denis", "seine saint denis", 
    "seine saint dinis", "paris", "val-de-marne", "val de marne", "hauts-de-seine", "hauts de seine", 
    "haut sde sein e", "haut de seine", "ardennes", "ardenne", "marne", "marnes", "meuse", 
    "meurthe-et-moselle", "meurthe et moselle", "côtes-d'armor", "cotes-d'armor", "cote d'armor", 
    "cote darmor", "seine-et-marne", "seine et marne", "essonne", "essone", "orne", "loir-et-cher", 
    "loir et cher", "yonne", "côte-d'or", "cote d'or", "cote dor", "nièvre", "nievre", "loiret", 
    "aube", "indre", "saône-et-loire", "saone et loire", "jura", "deux-sèvres", "deux sevres", 
    "deux-sevres", "vienne", "charente", "dordogne", "charente-maritime", "charente maritime", 
    "charnete maritime", "corrèze", "correze", "allier", "puy-de-dôme", "puy de dome", "doubs", 
    "cher", "vendée", "vendee", "hautes-pyrénées", "hautes pyrennes", "hautes-pyrenees", 
    "pyrénées-atlantiques", "pyrennes atlantiques", "pyrenees-atlantiques", "gers", "haute-garonne", 
    "haute garonne", "tarn", "aveyron", "aude", "gironde", "lot-et-garonne", "lot et garonne", 
    "tarn-et-garonne", "tarn et garonne", "lot", "hérault", "herault", "gard", "alpes-de-haute-provence", 
    "alpes de haute provence", "drôme", "drome", "savoie", "hautes-alpes", "hautes alpes", 
    "pyrénées-orientales", "pyrennes orientales", "pyrenees-orientales", "alpes-maritimes", 
    "alpes maritimes", "cantal", "lozère", "lozere", "vosges", "vosge", "isère", "isere", "ain", 
    "hain", "haute-savoie", "haute savoie", "moselle", "bas-rhin", "bas rhin", "haute-saône", 
    "haute saone", "haut saone", "vaucluse", "vauculse"
]

# 7. Style pour la couche départements
def determiner_style(feature):
    nom_dep = feature['properties'].get('nom', '').lower()
    if nom_dep in deps_75_85:
        color_fill = "#a0672a"
        fill_opacity = 0.85
    elif nom_dep in deps_85_95:
        color_fill = "#c8a96e"
        fill_opacity = 0.85
    else:
        color_fill = "#ffffff"
        fill_opacity = 1.0

    return {
        "fillColor": color_fill,
        "color": "none",
        "weight": 0,
        "fillOpacity": fill_opacity
    }

folium.GeoJson(
    geojson_departements,
    name="Couleurs Départements",
    style_function=determiner_style,
    interactive=False
).add_to(m)

# 8. Ajouter les contours EPCI
def style_epci(feature):
    return {
        "fillColor": "white",
        "fillOpacity": 0.0,
        "color": "#000000",
        "weight": 1.0
    }

def survol_epci(feature):
    return {
        "weight": 2.5,
        "color": "#333333"
    }

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

# 9. Script JavaScript : clic = contour rouge persistant
js_clic_epci = """
function(e) {
    var layer = e.target;
    var parent = layer._eventParents;
    for (var id in parent) {
        if (parent[id]._layers) {
            for (var subId in parent[id]._layers) {
                parent[id]._layers[subId].setStyle({
                    'color': '#000000',
                    'weight': 1.0
                });
            }
        }
    }
    layer.setStyle({
        'color': '#FF0000',
        'weight': 4.0
    });
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

# 9.5 Barre de recherche ajoutée sur la couche EPCI
Search(
    layer=geo_json_layer,
    geom_type="Polygon",
    placeholder="🔎 Rechercher un EPCI (entrez le nom)",
    search_label="nom",
    collapsed=False,
    position="topleft",
).add_to(m)

# 10. Affichage adaptatif de la carte dans Streamlit
st_folium(m, use_container_width=True, height=750)
