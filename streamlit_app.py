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
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

# --- JOUR ACTUEL ---
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
num_j = datetime.now().weekday()
nom_j = jours[num_j]

# --- PROMPT DE "VISION FORCÉE" ---
system_prompt = f"""
Tu es un extracteur de texte OCR haute précision. Ton unique but est de lire le bordereau de livraison.
Aujourd'hui nous sommes {nom_j}.

INSTRUCTIONS :
1. Analyse chaque ligne du tableau, même si c'est écrit petit.
2. Extrais CHAQUE client présent.
3. Pour chaque ligne, trouve :
   - Le NOM et PRENOM (Colonne 2).
   - L'ADRESSE (Colonne 3 : Rue, CP, Ville).
4. Pour le jour {nom_j} (Ligne {num_j + 1} des ronds) :
   - Si tu vois un 'N', écris 'PAS DE JOURNAL'.
   - Sinon, ne mets rien.

INTERDICTION : Ne fais pas de phrases. Ne dis pas que tu as oublié. 
S'il y a une image, extrais les données.
FORMAT DE SORTIE : NOM - ADRESSE - CONSIGNE
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
        
        # Maps Link
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
        <style>body {{ font-family: sans-serif; background: #f4f7f9; padding: 10px; }} h2 {{ color: #1a73e8; text-align: center; }}</style>
    </head>
    <body>
        <h2>🗞️ Tournée du {nom_j.upper()}</h2>
        {cards_html}
    </body>
    </html>
    """

st.title("🗞️ Scanner RL Universel")

file = st.file_uploader("Scan PDF ou Photo :", type=["pdf", "jpg", "png", "jpeg"])

if file:
    if st.button("🚀 ANALYSER LE BORDEREAU"):
        with st.spinner("L'IA analyse le document..."):
            try:
                if file.type == "application/pdf":
                    with pdfplumber.open(file) as pdf:
                        raw_content = "".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": raw_content}]
                    )
                else:
                    # Traitement Image
                    img = Image.open(file)
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}", "detail": "high"}}]}]
                    )
                
                st.session_state.res = response.choices[0].message.content
            except Exception as e:
                st.error(f"Erreur : {e}")

    if "res" in st.session_state:
        txt = st.text_area("Données extraites :", value=st.session_state.res, height=350)
        if st.button("⚙️ GÉNÉRER L'APPLI"):
            html = generate_final_html(txt.split("\n"))
            st.download_button("📥 TÉLÉCHARGER", html, "Tournee.html", "text/html")