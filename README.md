import streamlit as st
from openai import OpenAI
import pdfplumber
from PIL import Image
import base64
import io
from datetime import datetime

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Clé API manquante.")
    st.stop()

# --- GESTION DU JOUR ---
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
num_jour = datetime.now().weekday()
nom_jour = jours[num_jour]

# --- PROMPT POUR L'IA (UTILISÉ POUR PHOTO OU PDF) ---
system_prompt = f"""
Tu es un expert en logistique. Aujourd'hui nous sommes {nom_jour}.
Analyse les données fournies (texte ou image).

MISSION :
1. Extrais TOUS les clients (il y en a environ 19).
2. Pour chaque client : NOM, ADRESSE (Rue, CP, Ville).
3. Regarde le calendrier des jours (Ronds/N) : 
   - Ligne 1=Lundi, 2=Mardi, 3=Mercredi, 4=Jeudi, 5=Vendredi, 6=Samedi, 7=Dimanche.
   - Si 'N' sur la ligne de {nom_jour} -> 'PAS DE JOURNAL'.
   - Sinon -> ''.

FORMAT DE SORTIE : NOM - ADRESSE - CONSIGNE
"""

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if " - " not in line: continue
        parts = line.split(" - ")
        nom, adr = parts[0].strip().upper(), parts[1].strip().upper()
        ins = parts[2].strip() if len(parts) > 2 else ""
        
        is_stop = "PAS" in ins.upper()
        color = "#ef4444" if is_stop else "#1a73e8"
        bg = "#fff1f2" if is_stop else "#ffffff"
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

file = st.file_uploader("Dépose le PDF ou la Photo du bordereau :", type=["pdf", "jpg", "png", "jpeg"])

if file:
    if st.button("🚀 ANALYSER LE DOCUMENT"):
        with st.spinner("Analyse en cours..."):
            raw_content = ""
            
            # SI C'EST UN PDF
            if file.type == "application/pdf":
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        raw_content += page.extract_text()
                
                # On envoie le texte extrait à l'IA pour le mettre en forme
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": raw_content}]
                )
            
            # SI C'EST UNE PHOTO
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

    if "res" in st.session_state:
        txt = st.text_area("Vérification :", value=st.session_state.res, height=300)
        if st.button("⚙️ GÉNÉRER L'APPLI"):
            html = generate_final_html(txt.split("\n"))
            st.download_button("📥 TÉLÉCHARGER", html, "Tournee.html", "text/html")