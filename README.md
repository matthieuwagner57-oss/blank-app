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
    st.error("Erreur : Clé API manquante.")
    st.stop()

# --- DETERMINATION DU JOUR ACTUEL ---
jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
num_jour_actuel = datetime.now().weekday() # 0 = Lundi, 1 = Mardi...
nom_jour_actuel = jours_semaine[num_jour_actuel]

# --- PROMPT ULTRA-PUISSANT ---
system_prompt = f"""
Tu es un expert en lecture de bordereaux de livraison de journaux. 
Aujourd'hui nous sommes {nom_jour_actuel}.

CONSIGNES DE LECTURE :
1. Ignore la 1ère colonne (numéros/codes).
2. Colonne 2 : Extrais le NOM et PRENOM (ex: MME BERNADETTE BOUR). Sois très précis sur l'orthographe.
3. Colonne 3 : Extrais l'ADRESSE complète (Rue, Code Postal, Ville). Ne simplifie rien.
4. Colonne des ronds/N : 
   - La 1ère ligne de ronds correspond au Lundi.
   - La 2ème au Mardi, etc.
   - Regarde UNIQUEMENT la ligne du {nom_jour_actuel}.
   - Si tu vois un 'N' sur cette ligne, la consigne est "PAS DE JOURNAL CE {nom_jour_actuel.upper()}".
   - Sinon, laisse vide.

FORMAT DE SORTIE (STRICT) :
NOM - ADRESSE - CONSIGNE
"""

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if " - " not in line: continue
        parts = line.split(" - ")
        nom = parts[0].strip()
        adr = parts[1].strip()
        ins = parts[2].strip() if len(parts) > 2 else ""
        
        # Style alerte si PAS de journal
        is_stop = "PAS" in ins.upper()
        style_card = 'style="border-left: 8px solid #ef4444; background: #fff1f2;"' if is_stop else 'style="border-left: 8px solid #1a73e8;"'
        badge_ins = f'<div class="ins" style="background:#ef4444; color:white; padding:5px; border-radius:5px; font-weight:bold; margin-top:10px;">⚠️ {ins}</div>' if is_stop else ""

        maps_url = f"https://www.google.com/maps/search/?api=1&query={adr.replace(' ', '+')}"
        
        cards_html += f"""
        <div class="item">
            <input type="checkbox" id="c{i}" class="cb">
            <label for="c{i}" class="card" {style_card}>
                <div class="c-body">
                    <div class="nom-client">{nom}</div>
                    <div class="adr">{adr}</div>
                    {badge_ins}
                    <div class="v-btn">Valider la livraison</div>
                    <div class="f-btn">✅ FAIT</div>
                </div>
                <div class="c-act">
                    <a href="{maps_url}" class="m-btn" target="_blank" onclick="event.stopPropagation();">📍 Maps</a>
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
        .btn-r {{ background: #fee2e2; border: 1px solid #ef4444; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #dc2626; cursor: pointer; }}
        .btn-c {{ background: #f3f4f6; border: 1px solid #9ca3af; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #4b5563; cursor: pointer; }}
        #compact-toggle {{ display: none; }}
        #compact-toggle:checked ~ form .card {{ padding: 10px 15px; }}
        #compact-toggle:checked ~ form .v-btn, #compact-toggle:checked ~ form .f-btn {{ display: none !important; }}
        .list {{ display: flex; flex-direction: column; gap: 15px; max-width: 500px; margin: auto; }}
        .card {{ background: white; border-radius: 15px; padding: 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 6px rgba(0,0,0,0.05); cursor: pointer; }}
        .nom-client {{ font-size: 18px; font-weight: 900; color: #1a73e8; text-transform: uppercase; }}
        .adr {{ font-size: 14px; font-weight: 600; color: #4b5563; }}
        .v-btn {{ margin-top: 15px; display: inline-block; padding: 10px 20px; border-radius: 25px; background: #1a73e8; color: white; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        .f-btn {{ display: none; margin-top: 15px; padding: 10px 20px; border-radius: 25px; background: #22c55e; color: white; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
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
    <div class="header">🗞️ MA TOURNÉE DU {nom_jour_actuel.upper()}</div>
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
st.title("🗞️ Scanner RL Pro (Version GPT-4o)")

up = st.file_uploader("Photo du bordereau :", type=["jpg", "png", "jpeg"])

if up:
    if "raw_text" not in st.session_state:
        if st.button("🔍 ANALYSER LE BORDEREAU"):
            with st.spinner(f"Lecture précise pour {nom_jour_actuel}..."):
                img = Image.open(up)
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                # UTILISATION DE GPT-4o (BEAUCOUP PLUS PRECIS)
                response = client.chat.completions.create(
                    model="gpt-4o", # Changement ici : 'mini' était trop faible
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
                )
                st.session_state.raw_text = response.choices[0].message.content

    if "raw_text" in st.session_state:
        st.subheader("📝 Correction & Vérification")
        st.write(f"Jour détecté : **{nom_jour_actuel}**")
        corrected_text = st.text_area("Modifie si l'IA a fait une erreur :", value=st.session_state.raw_text, height=300)
        
        if st.button("🚀 GÉNÉRER L'APPLI DE TOURNÉE"):
            lines = corrected_text.split("\n")
            res_html = generate_final_html(lines)
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", res_html, "Tournee.html", "text/html")
            
            if st.button("🔄 Nouvelle analyse"):
                del st.session_state.raw_text
                st.rerun()