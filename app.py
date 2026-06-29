import streamlit as st

# Configuration de la page internet (mode large pour que ce soit beau)
st.set_page_config(
    page_title="Mon Application Cartographique", layout="wide", page_icon="🗺️"
)

# Titre principal de ton site web
st.title("Bienvenue sur mon application de cartographie ! 🗺️")

st.markdown("---")

# Message d'explication pour les utilisateurs
st.write("### 👈 Utilisez le menu à gauche pour naviguer")
st.write(
    "Dans le menu latéral, vous trouverez les différents codes et cartes interactives que j'ai préparés :"
)

# Liste de ce qu'il y a sur ton site
st.info("""
* **Page 1 : Carte Interactive** : Superposition des axes de ruissellement (Val-d'Oise) et des contours des EPCI avec surbrillance au survol.
* **Vos autres codes** : Ils apparaîtront juste en dessous dans le menu dès qu'on les aura ajoutés !
""")

st.markdown("---")
st.caption("Application développée en Python avec Streamlit et Folium.")
