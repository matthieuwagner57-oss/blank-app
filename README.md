import streamlit as st
from openai import OpenAI
from PIL import Image
import PyPDF2
import base64
import io
import re
import urllib.parse

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

# --- CONNEXION ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Erreur : Clé API manquante.")
    st.stop()

# --- LE PROMPT ULTIME ---
system_prompt = """
Tu es un expert développeur. Remplis ce modèle HTML sans toucher au CSS.
Pour chaque adresse lue :
1. Identifie l'ADRESSE et la CONSIGNE.
2. Crée le lien Maps : https://www.google.com/maps/search/?api=1&query=[ADRESSE_ENCODEE]

MODÈLE PAR ADRESSE :
<div class="card-wrapper">
    <input type="checkbox" id="check[ID]" class="card-input">
    <label for="check[ID]" class="card">
        <div class="card-body">
            <div class="address-text">[ADRESSE_MAJUSCULES]</div>
            <div class="special-instruction">[CONSIGNE_ROUGE_OU_VIDE]</div>
            <div class="valider-btn">Valider</div>
        </div>
        <div class="card-action">
            <a href="[LIEN_MAPS]" class="maps-btn" target="_blank" onclick="event.stopPropagation();">📍 Maps</a>
        </div>
    </label>
</div>
"""

# Le code HTML complet avec tout le style et les boutons magiques
html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ font-family: -apple-system, sans-serif; background-color: #f0f2f5; margin: 0; padding: 120px 15px 30px 15px; }}
        .header {{ position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 15px; text-align: center; z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }}
        .top-bar {{ position: fixed; top: 55px; left: 0; width: 100%; background: white; padding: 10px; display: flex; justify-content: center; gap: 10px; z-index: 999; border-bottom: 1px solid #ddd; }}
        .btn-opt {{ background: #f0f2f5; border: 1px solid #ccc; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; }}
        
        .card-list {{ display: flex; flex-direction: column; gap: 12px; max-width: 500px; margin: auto; }}
        .card {{ background: white; border-radius: 12px; padding: 15px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border-left: 6px solid #1a73e8; cursor: pointer; transition: 0.2s; -webkit-tap-highlight-color: transparent; }}
        .card-body {{ flex: 1; }}
        .address-text {{ font-size: 15px; font-weight: bold; color: #1c1e21; }}
        .special-instruction {{ color: #d93025; font-size: 12px; font-weight: bold; margin-top: 4px; text-transform: uppercase; }}
        .valider-btn {{ margin-top: 10px; display: inline-block; padding: 4px 12px; border-radius: 15px; border: 1px solid #1a73e8; color: #1a73e8; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
        
        .maps-btn {{ background: #1a73e8; color: white; padding: 10px 14px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: bold; display: flex; align-items: center; gap: 5px; }}
        
        /* ACTIONS */
        .card-input {{ display: none; }}
        .card-input:checked + .card {{ background: #e8eaed; border-left-color: #70757a; opacity: 0.6; transform: scale(0.97); }}
        .card-input:checked + .card .address-text {{ text-decoration: line-through; color: #70757a; }}
        .card-input:checked + .card .valider-btn {{ background: #70757a; color: white; border-color: #70757a; content: 'Livré'; }}
        .card-input:checked + .card .maps-btn {{ background: #70757a; }}

        /* VUE COMPACTE */
        body.compact .card {{ padding: 8px 15px; }}
        body.compact .valider-btn {{ display: none; }}
    </style>
</head>
<body id="mainBody">
    <div class="header">MA TOURNÉE RL</div>
    <div class="top-bar">
        <button class="btn-opt" onclick="window.location.reload()">🔄 TOUT DÉCOCHER</button>
        <button class="btn-opt" onclick="document.getElementById('mainBody').classList.toggle('compact')">🔍 VUE COMPACTE</button>
    </div>
    <div class="card-list">
        {content}
    </div>
</body>
</html>
"""

def ask_ai(data, is_image=False):
    content = [{"type": "text", "text": "Génère les cartes HTML pour ces adresses."}]
    if is_image:
        buffered = io.BytesIO()
        data.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}})
    else:
        content.append({"type": "text", "text": data})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": content}]
        )
        raw_res = response.choices[0].message.content
        cards = re.sub(r'```html|```', '', raw_res).strip()
        return html_template.format(content=cards)
    except Exception as e: return str(e)

# --- INTERFACE ---
st.title("🗞️ Tournée RL Finale")
tabs = st.tabs(["📸 Photo", "✍️ Manuel"])

with tabs[0]:
    up = st.file_uploader("Photo :", type=["jpg", "png", "jpeg"])
    if st.button("🚀 GÉNÉRER") and up:
        with st.spinner("Création de l'app..."):
            res = ask_ai(Image.open(up), is_image=True)
            st.download_button("📥 TÉLÉCHARGER L'APP", res, "Tournee.html", "text/html")

with tabs[1]:
    txt = st.text_area("Adresses :")
    if st.button("🚀 GÉNÉRER (TEXTE)") and txt:
        with st.spinner("Analyse..."):
            res = ask_ai(txt)
            st.download_button("📥 TÉLÉCHARGER L'APP", res, "Tournee.html", "text/html")