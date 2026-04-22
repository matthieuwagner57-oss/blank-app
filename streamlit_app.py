import streamlit as st
from openai import OpenAI
from PIL import Image
import PyPDF2
import base64
import io
import re

st.set_page_config(page_title="Générateur de Tournée", page_icon="🚚", layout="centered")

# --- CONNEXION ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Erreur : La clé OPENAI_API_KEY est absente.")
    st.stop()

# --- LE PROMPT "100% IDENTIQUE" ---
system_prompt = """
Tu es un robot chargé de remplir un modèle HTML. Tu ne dois rien inventer au design.
Tu vas lire la photo de la tournée et pour chaque ligne, tu vas générer le bloc HTML ci-dessous.

RÈGLES DE TRADUCTION :
- ADRESSE : Mets-la en MAJUSCULES.
- CONSIGNE : Si tu vois "Pas de journaux", "Pas le lundi", "Attention chien", etc., mets-le dans la zone consigne.
- MAPS : Crée le lien Google Maps vers l'adresse.

MODÈLE À RÉPÉTER POUR CHAQUE ADRESSE :
'''
<input type="checkbox" id="check[ID]" class="card-input">
<label for="check[ID]" class="card">
    <div class="card-content">
        <div class="address-text">[L'ADRESSE ICI]</div>
        <div class="special-instruction">[LA CONSIGNE EN ROUGE ICI OU VIDE]</div>
    </div>
    <div class="card-actions">
        <a href="https://www.google.com/maps/search/?api=1&query=[ADRESSE_URL]" class="maps-button" target="_blank">📍</a>
    </div>
</label>
'''

VOICI LE CODE COMPLET (HTML + CSS) QUE TU DOIS RENVOYER (SANS AUCUN TEXTE AUTOUR) :
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: sans-serif; background-color: #f0f2f5; margin: 0; padding: 70px 15px 20px 15px; }
        .header { position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 15px; font-weight: bold; text-align: center; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .card-list { display: flex; flex-direction: column; gap: 12px; }
        .card { background: white; border-radius: 10px; padding: 16px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer; border-left: 5px solid #1a73e8; }
        .card-content { flex: 1; }
        .address-text { font-size: 15px; font-weight: bold; color: #1c1e21; }
        .special-instruction { color: #d93025; font-size: 13px; font-weight: bold; margin-top: 4px; }
        .maps-button { background: #1a73e8; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 20px; flex-shrink: 0; margin-left: 10px; }
        
        /* EFFET QUAND ON COCHE */
        .card-input { display: none; }
        .card-input:checked + .card { background: #e8eaed; border-left-color: #70757a; opacity: 0.6; }
        .card-input:checked + .card .address-text { text-decoration: line-through; color: #70757a; }
        .card-input:checked + .card .maps-button { background: #70757a; }
    </style>
</head>
<body>
    <div class="header">MA TOURNÉE RL</div>
    <div class="card-list">
        [ICI TU INSERES TOUTES LES CARTES GÉNÉRÉES]
    </div>
</body>
</html>
"""

def clean_html(raw_html):
    return re.sub(r'```html|```', '', raw_html).strip()

def ask_ai_image(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
        )
        return clean_html(response.choices[0].message.content), None
    except Exception as e: return None, str(e)

# --- INTERFACE ---
st.title("🚚 Application Tournée RL")
up = st.file_uploader("Prendre la photo :", type=["jpg", "png"])
if st.button("🚀 GÉNÉRER L'APP") and up:
    res, err = ask_ai_image(Image.open(up))
    if res:
        st.success("Application prête !")
        st.download_button("📥 TÉLÉCHARGER L'APP", res, "Tournee.html", "text/html")