import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import re
from datetime import datetime

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

# --- CONNEXION ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Erreur : Clé API manquante dans les Secrets.")
    st.stop()

# --- JOUR ACTUEL ---
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
nom_jour = jours[datetime.now().weekday()]

# --- PROMPT DE LECTURE COLONNE PAR COLONNE ---
system_prompt = f"""
Tu es un scanner de haute précision. Ta mission est d'extraire les données du tableau de livraison.
Aujourd'hui nous sommes {nom_jour}.

RÈGLES STRICTES :
1. Lis le tableau LIGNE PAR LIGNE.
2. COLONNE NOM : Prends le nom complet (ex: MME BERNADETTE BOUR).
3. COLONNE ADRESSE : Prends l'adresse exacte (ex: 38 RUE SAINT ANTOINE 57600 OETING). Ne confonds pas avec les autres villes du tableau !
4. COLONNE JOURS : Repère le 'N'.
   - Ligne 1 des ronds = Lundi, Ligne 2 = Mardi...
   - Si un 'N' est présent sur la ligne de {nom_jour}, écris 'PAS DE JOURNAL'.
   - Sinon, laisse vide.

FORMAT : NOM - ADRESSE - CONSIGNE
"""

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if " - " not in line: continue
        parts = line.split(" - ")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper()
        ins = parts[2].strip() if len(parts) > 2 else ""
        
        # Alerte visuelle pour le "N"
        is_stop = "PAS" in ins.upper()
        card_border = "#ef4444" if is_stop else "#1a73e8"
        card_bg = "#fff1f2" if is_stop else "#ffffff"
        badge = f'<div style="background:#ef4444; color:white; padding:4px; border-radius:4px; font-size:10px; margin-top:8px; font-weight:bold;">⚠️ {ins}</div>' if is_stop else ""

        # LIEN MAPS DYNAMIQUE
        clean_adr = adr.replace(" ", "+")
        maps_link = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        cards_html += f"""
        <div class="item">
            <input type="checkbox" id="c{i}" class="cb">
            <label for="c{i}" class="card" style="border-left: 8px solid {card_border}; background: {card_bg};">
                <div class="c-body">
                    <div class="nom-client">{nom}</div>
                    <div class="adr">{adr}</div>
                    {badge}
                    <div class="v-btn">Valider la livraison</div>
                    <div class="f-btn">✅ FAIT</div>
                </div>
                <div class="c-act">
                    <a href="{maps_link}" class="m-btn" target="_blank" onclick="event.stopPropagation();">📍 Maps</a>
                </div>
            </label>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #f4f7f9; margin: 0; padding: 140px 15px 30px 15px; }}
        .header {{ position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 15px; text-align: center; z-index: 1000; font-weight: bold; font-size: 18px; }}
        .top-bar {{ position: fixed; top: 50px; left: 0; width: 100%; background: white; padding: 12px; display: flex; justify-content: center; gap: 10px; z-index: 999; border-bottom: 1px solid #ddd; }}
        .btn-r {{ background: #fee2e2; border: 1px solid #ef4444; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #dc2626; }}
        .btn-c {{ background: #f3f4f6; border: 1px solid #9ca3af; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #4b5563; }}
        #compact-toggle {{ display: none; }}
        #compact-toggle:checked ~ form .card {{ padding: 10px 15px; }}
        #compact-toggle:checked ~ form .v-btn, #compact-toggle:checked ~ form .f-btn {{ display: none !important; }}
        .list {{ display: flex; flex-direction: column; gap: 15px; max-width: 500px; margin: auto; }}
        .card {{ background: white; border-radius: 15px; padding: 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 6px rgba(0,0,0,0.05); cursor: pointer; }}
        .nom-client {{ font-size: 16px; font-weight: 900; color: #1a73e8; }}
        .adr {{ font-size: 13px; font-weight: 600; color: #4b5563; }}
        .v-btn {{ margin-top: 15px; display: inline-block; padding: 8px 15px; border-radius: 25px; background: #1a73e8; color: white; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
        .f-btn {{ display: none; margin-top: 15px; padding: 8px 15px; border-radius: 25px; background: #22c55e; color: white; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
        .m-btn {{ background: white; border: 2px solid #1a73e8; color: #1a73e8; padding: 10px; border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 13px; }}
        .cb {{ display: none; }}
        .cb:checked + .card {{ background: #f1f5f9; border-left-color: #22c55e !important; opacity: 0.8; }}
        .cb:checked + .card .v-btn {{ display: none; }}
        .cb:checked + .card .f-btn {{ display: inline-block; }}
        .cb:checked + .card .nom-client, .cb:checked + .card .adr {{ text-decoration: line-through; color: #94a3b8; }}
    </style>
</head>
<body>
    <input type="checkbox" id="compact-toggle">
    <div class="header">🗞️ TOURNÉE DU {nom_jour.upper()}</div>
    <form id="tf">
        <div class="top-bar">
            <button type="reset" class="btn-r">🔄 RESET</button>
            <label for="compact-toggle" class="btn-c">🔍 COMPACT</label>
        </div>
        <div class="list">{cards_html}</div>
    </form>
</body>
</html>
    """

# --- INTERFACE ---
st.title(f"🗞️ Scanner RL - {nom_jour}")

up = st.file_uploader("Prendre la photo :", type=["jpg", "png", "jpeg"])

if up:
    if "raw_text" not in st.session_state:
        if st.button("🔍 ANALYSER LE TABLEAU"):
            with st.spinner("Analyse précise..."):
                img = Image.open(up)
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
                )
                st.session_state.raw_text = response.choices[0].message.content

    if "raw_text" in st.session_state:
        st.subheader("📝 Vérification Manuelle")
        corrected = st.text_area("Vérifie et corrige les noms ou les 'N' :", value=st.session_state.raw_text, height=300)
        
        if st.button("🚀 GÉNÉRER L'APPLI FINALE"):
            lines = corrected.split("\n")
            res_html = generate_final_html(lines)
            st.download_button("📥 TÉLÉCHARGER", res_html, "Tournee.html", "text/html")