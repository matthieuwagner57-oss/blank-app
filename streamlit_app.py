import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import re

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

# --- CONNEXION ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Erreur : Clé API manquante.")
    st.stop()

# --- PROMPT D'EXTRACTION (RETOURNE DU TEXTE BRUT POUR CORRECTION) ---
system_prompt = """
Tu es un robot d'extraction. Lis la photo et sors la liste sous ce format exact :
NOM - ADRESSE - CONSIGNE
S'il n'y a pas de consigne, laisse vide après le tiret.
Un client par ligne.
"""

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if not line.strip(): continue
        # On sépare le texte par les tirets
        parts = line.split(" - ")
        nom = parts[0].strip() if len(parts) > 0 else "Inconnu"
        adr = parts[1].strip() if len(parts) > 1 else ""
        ins = parts[2].strip() if len(parts) > 2 else ""
        
        cards_html += f"""
        <div class="item">
            <input type="checkbox" id="c{i}" class="cb">
            <label for="c{i}" class="card">
                <div class="c-body">
                    <div class="nom-client">{nom}</div>
                    <div class="adr">{adr}</div>
                    <div class="ins">{ins}</div>
                    <div class="v-btn">Valider la livraison</div>
                    <div class="f-btn">✅ FAIT</div>
                </div>
                <div class="c-act">
                    <a href="https://www.google.com/maps/search/?api=1&query={adr.replace(' ', '+')}" class="m-btn" target="_blank" onclick="event.stopPropagation();">📍 Maps</a>
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
        .header {{ position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 15px; text-align: center; z-index: 1000; font-weight: bold; border-bottom: 2px solid #0d47a1; }}
        .top-bar {{ position: fixed; top: 50px; left: 0; width: 100%; background: white; padding: 12px; display: flex; justify-content: center; gap: 10px; z-index: 999; border-bottom: 1px solid #ddd; }}
        .btn-r {{ background: #fee2e2; border: 1px solid #ef4444; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #dc2626; cursor: pointer; }}
        .btn-c {{ background: #f3f4f6; border: 1px solid #9ca3af; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #4b5563; cursor: pointer; }}
        #compact-toggle {{ display: none; }}
        #compact-toggle:checked ~ form .card {{ padding: 10px 15px; }}
        #compact-toggle:checked ~ form .v-btn, #compact-toggle:checked ~ form .f-btn {{ display: none !important; }}
        .list {{ display: flex; flex-direction: column; gap: 15px; max-width: 500px; margin: auto; }}
        .card {{ background: white; border-radius: 15px; padding: 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 8px solid #1a73e8; cursor: pointer; }}
        .nom-client {{ font-size: 18px; font-weight: 900; color: #1a73e8; text-transform: uppercase; }}
        .adr {{ font-size: 15px; font-weight: 600; color: #4b5563; }}
        .ins {{ color: #e11d48; font-size: 12px; font-weight: 800; margin-top: 8px; text-transform: uppercase; background: #fff1f2; padding: 4px 8px; border-radius: 4px; display: inline-block; }}
        .v-btn {{ margin-top: 15px; display: inline-block; padding: 8px 20px; border-radius: 25px; background: #1a73e8; color: white; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        .f-btn {{ display: none; margin-top: 15px; padding: 8px 20px; border-radius: 25px; background: #22c55e; color: white; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        .m-btn {{ background: white; border: 2px solid #1a73e8; color: #1a73e8; padding: 10px 14px; border-radius: 12px; text-decoration: none; font-weight: bold; }}
        .cb {{ display: none; }}
        .cb:checked + .card {{ background: #f1f5f9; border-left-color: #22c55e; opacity: 0.8; transform: scale(0.96); }}
        .cb:checked + .card .nom-client, .cb:checked + .card .adr {{ text-decoration: line-through; color: #94a3b8; }}
        .cb:checked + .card .v-btn {{ display: none; }}
        .cb:checked + .card .f-btn {{ display: inline-block; }}
    </style>
</head>
<body>
    <input type="checkbox" id="compact-toggle">
    <div class="header">🗞️ MA TOURNÉE RL</div>
    <form id="tf">
        <div class="top-bar">
            <button type="reset" class="btn-r">🔄 TOUT DÉCOCHER</button>
            <label for="compact-toggle" class="btn-c">🔍 VUE COMPACTE</label>
        </div>
        <div class="list">{cards_html}</div>
    </form>
</body>
</html>
    """

# --- INTERFACE ---
st.title("🗞️ Scanner RL Pro")

up = st.file_uploader("Photo de la feuille :", type=["jpg", "png", "jpeg"])

if up:
    if "raw_text" not in st.session_state:
        if st.button("🔍 ANALYSER LA PHOTO"):
            with st.spinner("Lecture..."):
                img = Image.open(up)
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
                )
                st.session_state.raw_text = response.choices[0].message.content

    if "raw_text" in st.session_state:
        st.subheader("📝 Correction des noms/adresses")
        st.info("L'IA peut faire des erreurs. Corrige les fautes ci-dessous avant de valider :")
        
        # Zone de texte pour corriger les erreurs de l'IA
        corrected_text = st.text_area("Vérifie bien les numéros et les noms :", value=st.session_state.raw_text, height=200)
        
        if st.button("🚀 CRÉER MON APPLICATION FINALE"):
            lines = corrected_text.split("\n")
            res_html = generate_final_html(lines)
            st.success("✅ Application prête !")
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", res_html, "Tournee.html", "text/html")
            # Optionnel : bouton pour recommencer
            if st.button("🔄 Nouvelle photo"):
                del st.session_state.raw_text
                st.rerun()

st.divider()
st.caption("Créé par Matthieu WAGNER")