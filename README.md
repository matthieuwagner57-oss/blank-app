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
    st.error("Clé API manquante.")
    st.stop()

# --- GESTION DU JOUR ---
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
nom_jour = jours[datetime.now().weekday()]

# --- PROMPT DE HAUTE PRÉCISION ---
system_prompt = f"""
Tu es un expert en logistique. Tu dois extraire TOUTES les lignes (environ 19) du bordereau.
Aujourd'hui nous sommes {nom_jour}.

CONSIGNES :
1. Extrais le NOM et l'ADRESSE (Rue, CP, Ville).
2. Pour chaque client, regarde la colonne des jours (Ronds et N).
3. La 1ère ligne de ronds est Lundi, la 2ème Mardi, etc.
4. Si tu vois un 'N' sur la ligne de {nom_jour} -> Écris 'PAS DE JOURNAL'.
5. Si c'est un rond 'O' -> Laisse vide.

FORMAT DE SORTIE : NOM - ADRESSE - CONSIGNE
"""

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if " - " not in line: continue
        parts = line.split(" - ")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper()
        ins = parts[2].strip() if len(parts) > 2 else ""
        
        is_stop = "PAS" in ins.upper()
        color = "#ef4444" if is_stop else "#1a73e8"
        bg = "#fff1f2" if is_stop else "#ffffff"
        
        # Lien Maps sécurisé
        maps_url = f"https://www.google.com/maps/search/?api=1&query={adr.replace(' ', '+')}"
        
        cards_html += f"""
        <div style="margin-bottom:12px; background:{bg}; border-left:8px solid {color}; padding:15px; border-radius:12px; box-shadow:0 2px 4px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center;">
            <div style="flex-grow:1;">
                <div style="font-size:16px; font-weight:900; color:#1a73e8;">{nom}</div>
                <div style="font-size:13px; font-weight:600; color:#4b5563;">{adr}</div>
                {f'<div style="color:#ef4444; font-weight:bold; font-size:11px; margin-top:5px;">⚠️ {ins}</div>' if is_stop else ''}
            </div>
            <a href="{maps_url}" target="_blank" style="margin-left:10px; background:white; border:2px solid #1a73e8; color:#1a73e8; padding:10px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:12px;">📍 MAPS</a>
        </div>
        """
    return f"<html><body style='font-family:sans-serif; background:#f4f7f9; padding:10px;'><h2 style='color:#1a73e8; text-align:center;'>🗞️ TOURNÉE {nom_jour.upper()}</h2>{cards_html}</body></html>"

# --- INTERFACE ---
st.title("🗞️ Scanner RL (Photo ou PDF)")

file = st.file_uploader("Dépose ton scan PDF ou ta Photo :", type=["pdf", "jpg", "png", "jpeg"])

if file:
    if st.button("🚀 ANALYSER LE DOCUMENT"):
        with st.spinner("Analyse des 19 lignes..."):
            if file.type == "application/pdf":
                with pdfplumber.open(file) as pdf:
                    raw_content = "".join([p.extract_text() for p in pdf.pages])
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": raw_content}]
                )
            else:
                img_str = base64.b64encode(file.read()).decode('utf-8')
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
                )
            st.session_state.res = response.choices[0].message.content

    if "res" in st.session_state:
        txt = st.text_area("Correction (Vérifie bien les 19 lignes) :", value=st.session_state.res, height=350)
        if st.button("⚙️ GÉNÉRER L'APPLI"):
            html = generate_final_html(txt.split("\n"))
            st.download_button("📥 TÉLÉCHARGER", html, "Tournee.html", "text/html")