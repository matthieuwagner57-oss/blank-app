import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import re

# ... (garder le début du code identique jusqu'à generate_final_html) ...

# --- INTERFACE MODIFIÉE POUR IPHONE ---
st.title("🗞️ Application Tournée RL")
up = st.file_uploader("Prendre la photo :", type=["jpg", "png", "jpeg"])

if st.button("🚀 GÉNÉRER L'APPLICATION") and up:
    with st.spinner("Analyse en cours..."):
        res = ask_ai(Image.open(up))
        
        # Option 1 : Téléchargement (pour Android)
        st.download_button("📥 TÉLÉCHARGER (Android)", res, "Tournee.html", "text/html")
        
        st.divider()
        
        # Option 2 : Affichage direct (POUR IPHONE)
        st.subheader("📱 Spécial iPhone (Si Indeed bloque)")
        st.markdown("Clique sur le lien ci-dessous, il va s'ouvrir DIRECTEMENT dans ton navigateur sans passer par Indeed :")
        
        # On transforme le code en un lien "Data" que Safari comprend direct
        b64 = base64.b64encode(res.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" target="_blank" style="padding: 20px; background-color: #1a73e8; color: white; text-decoration: none; border-radius: 10px; display: block; text-align: center; font-weight: bold;">🚀 OUVRIR L\'APPLI DIRECTEMENT</a>'
        st.markdown(href, unsafe_allow_html=True)

st.caption("Créé par Matthieu WAGNER - Version Anti-Indeed")