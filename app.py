import streamlit as st

# Configuration de la page internet (mode large pour que ce soit beau)
st.set_page_config(
    page_title="Mon Application Cartographique", layout="wide", page_icon="🗺️"
)

# Titre principal de ton site web
st.title("Bienvenue sur la Web App Résilience Inondation! 🗺️")

st.markdown("---")

# Message d'explication pour les utilisateurs
st.write("### 👈 Utilisez le menu à gauche pour naviguer")
st.write(
    "Dans le menu latéral, vous trouverez les différents codes et cartes interactives  :"
)

# Liste de ce qu'il y a sur ton site
st.info("""
* **Page 1  Carte Interactive** : Contours des EPCI
* **Page 2 Carte Interactive**:  Nombre d'arrêtés CATNAT (cumulés sur la pèriode 2000-2026) pour le péril "Inondations et/ou Coulées de Boue"
* **Page 3 Carte Interactive**: Moyenne des zonages Inondation par EPCI
* **Page 4 Carte Interactive**: Axes de ruissellement pour le Val d'Oise (95)
* **Page 5 Carte Interactive**: Cumul annuel de précipitations modérées: rapport % à référence 1976-2005 pour l'horizon lointain (2071-2100)
* **Page 6 Carte Interactive**: Exposition au Ruissellement

""")

st.markdown("---")
st.caption("Application développée en Python avec Streamlit et Folium.")
