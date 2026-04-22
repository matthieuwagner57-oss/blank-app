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

# --- LE PROMPT "DESIGN PARFAIT" ---
# Ce prompt force l'IA à utiliser le code exact de ma démo
system_prompt = """
Tu es un expert développeur. Ton unique mission est de remplir le modèle HTML ci-dessous avec les adresses trouvées.
INTERDICTION de changer le CSS ou la structure.

RELIRE LA PHOTO/TEXTE :
1. Liste chaque adresse.
2. Identifie les consignes (ex: 'Pas de journaux', 'Pas le lundi').
3. Génère le lien Google Maps : https://www.google.com/maps/search/?api=1&query=[ADRESSE_ENCODÉE]

STRUCTURE DE CHAQUE CARTE :
<input type="checkbox" id="check[ID]" class="card-input">
<label for="check[ID]" class="card">
    <div class="card-content">
        <div class="address-text">[L'ADRESSE ICI EN MAJUSCULES]</div>
        <div class="special-instruction">[LA CONSIGNE EN ROUGE SI ELLE EXISTE SINON VIDE]</div>
    </div>
    <div class="card-actions">
        <a href="https://www.google.com/maps/search/?api=1&query=[ADRESSE]" class="maps-button" target="_blank">📍</a>
    </div>
</label>

RENVOIE UNIQUEMENT LE CODE HTML COMPLET :
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: -apple-system, sans-serif; background-color: #f0f2f5; margin: 0; padding: 75px 15px 30px 15px; }
        .header { position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 18px; font-weight: bold; text-align: center; z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-size: 18px; }
        .card-list { display: flex; flex-direction: column; gap: 12px; max-width: 500px; margin: auto; }
        .card { background: white; border-radius: 12px; padding: 18px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 6px rgba(0,0,0,0.08); cursor: pointer; border-left: 6px solid #1a73e8; transition: 0.2s; }
        .card-content { flex: 1; pointer-events: none; }
        .address-text { font-size: 16px; font-weight: bold; color: #1c1e21; line-height: 1.3; }
        .special-instruction { color: #d93025; font-size: 13px; font-weight: bold; margin-top: 6px; text-transform: uppercase; }
        .card-actions { margin-left: 15px; }
        .maps-button { background: #1a73e8; color: white; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 22px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        
        /* EFFET COCHÉ */
        .card-input { display: none; }
        .card-input:checked + .card { background: #e8eaed; border-left-color: #70757a; opacity: 0.5; box-shadow: none; transform: scale(0.98); }
        .card-input:checked + .card .address-text { text-decoration: line-through; color: #70757a; }
        .card-input:checked + .card .maps-button { background: #70757a; }
    </style>
</head>
<body>
    <div class="header">MA TOURNÉE RL</div>
    <div class="card-list">
        [TES_CARTES_ICI]
    </div>
</body>
</html>
"""

# --- FONCTION NETTOYAGE ---
def clean_html(raw_html):
    return re.sub(r'```html|```', '', raw_html).strip()

# --- FONCTIONS AI ---
def ask_ai_text(text_data):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text_data}]
        )
        return clean_html(response.choices[0].message.content), None
    except Exception as e: return None, str(e)

def ask_ai_image(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": [{"type": "text", "text": "Analyse cette photo :"}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
        )
        return clean_html(response.choices[0].message.content), None
    except Exception as e: return None, str(e)

# --- INTERFACE STREAMLIT ---
st.title("🗞️ Application Tournée RL")
st.markdown("Générez votre liste de livraison interactive.")

tabs = st.tabs(["📸 Photo", "📄 PDF / Texte", "✍️ Manuel"])

# ONGLET PHOTO
with tabs[0]:
    up_img = st.file_uploader("Prendre en photo la feuille :", type=["jpg", "png", "jpeg"])
    if st.button("🚀 GÉNÉRER DEPUIS PHOTO") and up_img:
        with st.spinner("Analyse de l'image en cours... patientez..."):
            res, err = ask_ai_image(Image.open(up_img))
            if res:
                st.success("Application prête !")
                st.download_button("📥 TÉLÉCHARGER MON APP", res, "Tournee.html", "text/html")
            else: st.error(err)

# ONGLET PDF
with tabs[1]:
    up_file = st.file_uploader("Uploader un fichier :", type=["pdf", "txt"])
    if st.button("🚀 GÉNÉRER DEPUIS FICHIER") and up_file:
        with st.spinner("Lecture du fichier..."):
            txt = ""
            if up_file.name.endswith(".pdf"):
                pdf = PyPDF2.PdfReader(up_file)
                for p in pdf.pages: txt += p.extract_text()
            else: txt = up_file.read().decode()
            res, err = ask_ai_text(txt)
            if res: st.download_button("📥 TÉLÉCHARGER MON APP", res, "Tournee.html", "text/html")

# ONGLET MANUEL
with tabs[2]:
    txt_input = st.text_area("Coller les adresses ici :")
    if st.button("🚀 GÉNÉRER DEPUIS TEXTE") and txt_input:
        with st.spinner("Analyse du texte..."):
            res, err = ask_ai_text(txt_input)
            if res: st.download_button("📥 TÉLÉCHARGER MON APP", res, "Tournee.html", "text/html")

st.divider()
st.caption("Créé par Matthieu WAGNER - Version Finale Stabilité")