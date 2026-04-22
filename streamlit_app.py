import streamlit as st
from openai import OpenAI
import pdfplumber
from PIL import Image
import base64
import io
from datetime import datetime

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

# --- CONNEXION ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Erreur : Clé API manquante dans les Secrets.")
    st.stop()

# --- GESTION DU JOUR ---
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
num_jour_actuel = datetime.now().weekday()
nom_jour_actuel = jours[num_jour_actuel]

# --- PROMPT UNIVERSEL ---
system_prompt = f"""
Tu es un assistant logistique expert. Analyse ce bordereau de livraison.
Aujourd'hui nous sommes {nom_jour_actuel}.

INSTRUCTIONS :
1. Extrais TOUTES les lignes de livraison visibles.
2. Pour chaque ligne, identifie :
   - Le NOM et PRENOM du client.
   - L'ADRESSE complète (Rue, Code Postal, Ville).
3. Regarde la grille des jours (ronds et N) :
   - Si tu vois un 'N' sur la ligne correspondant au {nom_jour_actuel}, note 'PAS DE JOURNAL'.
   - Sinon, ne note rien.

SORTIE : NOM - ADRESSE - CONSIGNE
(Un client par ligne)
"""

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if " - " not in line: continue
        parts = line.split(" - ")
        if len(parts) < 2: continue
        
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper()
        ins = parts[2].strip() if len(parts) > 2 else ""
        
        is_stop = "PAS" in ins.upper()
        color = "#ef4444" if is_stop else "#1a73e8"
        bg = "#fff1f2" if is_stop else "#ffffff"
        
        # Lien Maps Universel (Search API)
        clean_adr = adr.replace(" ", "+")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        cards_html += f"""
        <div style="margin-bottom:12px; background:{bg}; border-left:8px solid {color}; padding:15px; border-radius:12px; box-shadow:0 2px 4px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center;">
            <div style="flex-grow:1;">
                <div style="font-size:16px; font-weight:900; color:#1a73e8;">{nom}</div>
                <div style="font-size:13px; font-weight:600; color:#4b5563;">{adr}</div>
                {f'<div style="color:#ef4444; font-weight:bold; font-size:11px; margin-top:5px;">⚠️ {ins}</div>' if is_stop else ''}
            </div>
            <a href="{maps_url}" target="_blank" style="margin-left:10px; background:white; border:2px solid #1a73e8; color:#1a73e8; padding:12px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:14px; text-align:center;">📍 MAPS</a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #f4f7f9; padding: 10px; margin: 0; }}
            h2 {{ color: #1a73e8; text-align: center; font-size: 20px; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <h2>🗞️ Tournée du {nom_jour_actuel.upper()}</h2>
        {cards_html}
    </body>
    </html>
    """

# --- INTERFACE ---
st.title("🗞️ Scanner RL Universel")
st.write(f"Analyse pour le : **{nom_jour_actuel}**")

file = st.file_uploader("Photo ou Scan PDF du bordereau :", type=["pdf", "jpg", "png", "jpeg"])

if file:
    if st.button("🔍 ANALYSER LE BORDEREAU"):
        with st.spinner("Analyse en cours..."):
            try:
                if file.type == "application/pdf":
                    with pdfplumber.open(file) as pdf:
                        raw_content = "".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": raw_content}]
                    )
                else:
                    img = Image.open(file)
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
                    )
                
                st.session_state.res = response.choices[0].message.content
            except Exception as e:
                st.error(f"Erreur lors de l'analyse : {e}")

    if "res" in st.session_state:
        st.subheader("📝 Correction & Vérification")
        txt = st.text_area("Vérifie les données lues :", value=st.session_state.res, height=350)
        
        if st.button("⚙️ GÉNÉRER L'APPLI DE TOURNÉE"):
            html = generate_final_html(txt.split("\n"))
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", html, "Tournee.html", "text/html")
            st.success("Fichier prêt ! Ouvre-le sur ton téléphone.")