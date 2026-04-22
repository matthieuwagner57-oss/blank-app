import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
from datetime import datetime

st.set_page_config(page_title="Scanner Tournée RL", page_icon="🗞️")

# --- CONNEXION ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Clé API manquante dans Streamlit Secrets.")
    st.stop()

# --- PROMPT (LE MÊME QUI MARCHAT AU DÉBUT) ---
system_prompt = """
Tu es un expert en lecture de documents. 
Regarde la photo du bordereau de livraison.
Pour chaque client, extrais : NOM - ADRESSE COMPLETE.
Sois très précis sur l'orthographe des noms et des rues à OETING.
Ne fais pas de commentaires, donne juste la liste.
Format : NOM - ADRESSE
"""

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if " - " not in line: continue
        parts = line.split(" - ")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper()
        
        clean_adr = adr.replace(" ", "+")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        cards_html += f"""
        <div style="margin-bottom:12px; background:white; border-left:8px solid #1a73e8; padding:15px; border-radius:12px; box-shadow:0 2px 4px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center;">
            <div style="flex-grow:1;">
                <div style="font-size:16px; font-weight:900; color:#1a73e8;">{nom}</div>
                <div style="font-size:13px; font-weight:600; color:#4b5563;">{adr}</div>
                <div style="margin-top:10px; display:inline-block; padding:5px 15px; background:#1a73e8; color:white; border-radius:15px; font-size:10px; font-weight:bold;">À LIVRER</div>
            </div>
            <a href="{maps_url}" target="_blank" style="margin-left:10px; background:white; border:2px solid #1a73e8; color:#1a73e8; padding:10px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:12px; text-align:center;">📍 MAPS</a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family:sans-serif; background:#f4f7f9; padding:10px;">
        <h2 style="color:#1a73e8; text-align:center;">MA TOURNÉE DE LIVRAISON</h2>
        {cards_html}
    </body>
    </html>
    """

st.title("🗞️ Scanner RL Pro")

up = st.file_uploader("Prendre la photo du bordereau", type=["jpg", "png", "jpeg"])

if up:
    if st.button("🔍 ANALYSER LA PHOTO"):
        with st.spinner("Lecture en cours..."):
            img = Image.open(up)
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
            )
            st.session_state.text_result = response.choices[0].message.content

    if "text_result" in st.session_state:
        # L'étape cruciale : tu peux corriger les noms ici si l'IA s'est trompée
        corrected = st.text_area("Vérifie les adresses avant de valider :", value=st.session_state.text_result, height=300)
        
        if st.button("🚀 CRÉER L'APPLI POUR MON TÉLÉPHONE"):
            html_code = generate_final_html(corrected.split("\n"))
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", html_code, "MaTournee.html", "text/html")
            st.info("Une fois téléchargé, envoie ce fichier par mail à ton téléphone !")