import streamlit as st
from openai import OpenAI
from PIL import Image
import PyPDF2
import base64
import io
import re

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

# --- CONNEXION OPENAI ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Erreur : Clé API manquante dans les Secrets.")
    st.stop()

# --- LE PROMPT "MOULE FIGÉ" (CONCEPTION STRICTE) ---
# J'ai figé mon design exact dans ce prompt pour que l'IA ne puisse rien changer au style.
system_prompt = """
Tu es un robot chargé de remplir un modèle HTML. Tu ne dois RIEN changer au design (CSS).
Ta seule mission est de lire la photo de la tournée et de générer une carte HTML pour CHAQUE adresse trouvée, en utilisant EXACTEMENT le modèle ci-dessous.

MODÈLE HTML À RÉPÉTER POUR CHAQUE ADRESSE :
'''
<div class="card">
    <div class="card-check">
        <input type="checkbox" class="delivery-checkbox" id="check[ID_UNIQUE]">
    </div>
    <div class="card-body">
        <div class="card-address">[L'ADRESSE COMPLÈTE EN MAJUSCULES]</div>
        <div class="card-instruction">[LA CONSIGNE SPÉCIALE EN ROUGE, OU VIDE SI AUCUNE]</div>
    </div>
    <div class="card-action">
        <a href="http://googleusercontent.com/maps.google.com/6" class="maps-btn" target="_blank">📍 Google Maps</a>
    </div>
</div>
'''

RÈGLES DE REMPLISSAGE :
1. Analyse la photo fournie (ex: celle de Forbach).
2. Pour chaque ligne, crée une carte en remplaçant :
   - [L'ADRESSE COMPLÈTE EN MAJUSCULES] par l'adresse lue (ex: 13 RUE DU ROCHER, 57600 FORBACH).
   - [LA CONSIGNE SPÉCIALE EN ROUGE] par la consigne si détectée (ex: 'Pas de journaux le lundi').
   - Le lien Google Maps par l'adresse encodée.
3. Ne renvoie AUCUN texte avant ou après le code <html>.

VOICI LE CODE HTML COMPLET QUE TU DOIS RENVOYER (AVEC LE DESIGN FIGÉ) :
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: -apple-system, system-serif; background-color: #f6f8fa; margin: 0; padding: 70px 15px 20px 15px; color: #1c1e21; }
        .header { position: fixed; top: 0; left: 0; width: 100%; background: white; padding: 15px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); z-index: 1000; }
        .header-title { font-size: 18px; font-weight: bold; margin: 0; }
        .header-subtitle { font-size: 14px; color: #65676b; margin-top: 2px; }
        .card-list { display: flex; flex-direction: column; gap: 15px; max-width: 500px; margin: auto; }
        .card { background: white; border-radius: 12px; padding: 18px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,0,0,0.08); transition: 0.2s; }
        .card-check { margin-right: 15px; }
        .delivery-checkbox { width: 22px; height: 22px; cursor: pointer; }
        .card-body { flex: 1; margin-right: 15px; }
        .card-address { font-size: 16px; font-weight: 700; line-height: 1.3; }
        .card-instruction { color: #d93025; font-size: 13px; font-weight: bold; margin-top: 5px; }
        .card-action { flex-shrink: 0; }
        .maps-btn { background-color: #1a73e8; color: white; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }
        
        /* EFFET QUAND ON COCHE L'ADRESSE */
        .card:has(.delivery-checkbox:checked) { background-color: #f0f2f5; opacity: 0.6; box-shadow: none; filter: grayscale(100%); }
        .card:has(.delivery-checkbox:checked) .card-address { text-decoration: line-through; color: #65676b; }
        .card:has(.delivery-checkbox:checked) .maps-btn { background-color: #8c9199; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">Ma Tournée RL</div>
        <div class="header-subtitle">Cliquez sur Maps pour l'itinéraire</div>
    </div>
    <div class="card-list">
        [TES_CARTES_ICI]
    </div>
</body>
</html>
"""

# --- FONCTION NETTOYAGE ---
def clean_html(raw_html):
    cleaned = re.sub(r'```html', '', raw_html)
    cleaned = re.sub(r'```', '', cleaned)
    return cleaned.strip()

# --- FONCTIONS AI (AMÉLIORÉES) ---
def ask_ai_text(text_data):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text_data}]
        )
        return clean_html(response.choices[0].message.content), None
    except Exception as e: return None, str(e)

def ask_ai_image(img):
    try:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": [{"type": "text", "text": "Analyse cette photo de tournée pour remplir le moule :"}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
        )
        return clean_html(response.choices[0].message.content), None
    except Exception as e: return None, str(e)

# --- INTERFACE STREAMLIT ---
st.title("🗞️ Application Tournée RL (Version Finale)")
st.markdown("Générez votre liste de livraison interactive à l'identique de la démo.")

tabs = st.tabs(["📸 Photo", "📄 PDF / Texte", "✍️ Manuel"])

# ONGLET PHOTO
with tabs[0]:
    up_img = st.file_uploader("Prendre en photo la feuille de tournée :", type=["jpg", "png", "jpeg"])
    if st.button("🚀 GÉNÉRER DEPUIS PHOTO") and up_img:
        with st.spinner("Analyse et remplissage du moule en cours..."):
            res, err = ask_ai_image(Image.open(up_img))
            if res:
                st.success("Application générée avec succès !")
                st.download_button("📥 TÉLÉCHARGER MON APP (HTML)", res, "Tournee.html", "text/html")
            else: st.error(f"Erreur technique : {err}")

# ONGLET PDF
with tabs[1]:
    up_file = st.file_uploader("Uploader un fichier :", type=["pdf", "txt"])
    if st.button("🚀 GÉNÉRER DEPUIS FICHIER") and up_file:
        with st.spinner("Lecture et analyse..."):
            txt = ""
            if up_file.name.endswith(".pdf"):
                pdf = PyPDF2.PdfReader(up_file)
                for p in pdf.pages: txt += p.extract_text()
            else: txt = up_file.read().decode()
            res, err = ask_ai_text(txt)
            if res: st.download_button("📥 TÉLÉCHARGER MON APP (HTML)", res, "Tournee.html", "text/html")

# ONGLET MANUEL
with tabs[2]:
    txt_input = st.text_area("Coller les adresses ici :")
    if st.button("🚀 GÉNÉRER DEPUIS TEXTE") and txt_input:
        with st.spinner("Analyse du texte..."):
            res, err = ask_ai_text(txt_input)
            if res: st.download_button("📥 TÉLÉCHARGER MON APP (HTML)", res, "Tournee.html", "text/html")

st.divider()
st.caption("Créé par Matthieu WAGNER - Version Finale Identique")