import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from PIL import Image
import base64
import io
import re

# On force le mode large pour que ça ressemble à une vraie page sur mobile
st.set_page_config(page_title="Générateur RL", page_icon="🗞️", layout="wide")

# --- CONNEXION ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Erreur : Clé API manquante.")
    st.stop()

# --- LE PROMPT ---
system_prompt = """
Tu es un robot d'extraction. Pour chaque ligne lue, génère UNIQUEMENT ce bloc HTML.
Affiche le NOM en gros et l'ADRESSE juste en dessous.

MODÈLE :
<div class="item">
    <input type="checkbox" id="c[ID]" class="cb">
    <label for="c[ID]" class="card">
        <div class="c-body">
            <div class="nom">[NOM]</div>
            <div class="adr">[ADRESSE]</div>
            <div class="ins">[CONSIGNE_OU_VIDE]</div>
            <div class="v-btn">Valider la livraison</div>
            <div class="f-btn">✅ FAIT</div>
        </div>
        <div class="c-act">
            <a href="https://www.google.com/maps/search/?api=1&query=[ADRESSE_URL]" class="m-btn" target="_blank">📍 Maps</a>
        </div>
    </label>
</div>
"""

def generate_final_html(cards_html):
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #f4f7f9; margin: 0; padding: 120px 10px 20px 10px; }}
        .header {{ position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 15px; text-align: center; z-index: 1000; font-weight: bold; border-bottom: 2px solid #0d47a1; }}
        .top-bar {{ position: fixed; top: 48px; left: 0; width: 100%; background: white; padding: 10px; display: flex; justify-content: center; gap: 10px; z-index: 999; border-bottom: 1px solid #ddd; }}
        .btn-r {{ background: #fee2e2; border: 1px solid #ef4444; padding: 8px 15px; border-radius: 20px; font-size: 11px; font-weight: bold; color: #dc2626; }}
        .btn-c {{ background: #f3f4f6; border: 1px solid #9ca3af; padding: 8px 15px; border-radius: 20px; font-size: 11px; font-weight: bold; color: #4b5563; }}
        #compact-toggle {{ display: none; }}
        #compact-toggle:checked ~ form .card {{ padding: 10px; }}
        #compact-toggle:checked ~ form .v-btn, #compact-toggle:checked ~ form .f-btn {{ display: none !important; }}
        .list {{ display: flex; flex-direction: column; gap: 10px; }}
        .card {{ background: white; border-radius: 12px; padding: 18px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 6px solid #1a73e8; }}
        .nom {{ font-size: 16px; font-weight: 800; color: #1a73e8; text-transform: uppercase; }}
        .adr {{ font-size: 14px; color: #4b5563; font-weight: 600; }}
        .v-btn {{ margin-top: 10px; display: inline-block; padding: 8px 15px; border-radius: 20px; background: #1a73e8; color: white; font-size: 11px; font-weight: bold; }}
        .f-btn {{ display: none; margin-top: 10px; padding: 8px 15px; border-radius: 20px; background: #22c55e; color: white; font-size: 11px; font-weight: bold; }}
        .m-btn {{ background: white; border: 1.5px solid #1a73e8; color: #1a73e8; padding: 8px 12px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 13px; }}
        .cb {{ display: none; }}
        .cb:checked + .card {{ background: #f8fafc; border-left-color: #22c55e; opacity: 0.8; }}
        .cb:checked + .card .v-btn {{ display: none; }}
        .cb:checked + .card .f-btn {{ display: inline-block; }}
        .cb:checked + .card .nom, .cb:checked + .card .adr {{ text-decoration: line-through; color: #94a3b8; }}
    </style>
</head>
<body>
    <input type="checkbox" id="compact-toggle">
    <div class="header">🗞️ MA TOURNÉE RL</div>
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

def ask_ai(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}]}]
    )
    cards = re.sub(r'```html|```', '', response.choices[0].message.content).strip()
    return generate_final_html(cards)

# --- INTERFACE ---
st.title("🗞️ Scanner RL")

up = st.file_uploader("Photo de la feuille :", type=["jpg", "png", "jpeg"])

if up:
    if st.button("🚀 GÉNÉRER LA TOURNÉE"):
        with st.spinner("Analyse en cours..."):
            res_html = ask_ai(Image.open(up))
            
            # --- LA SOLUTION FINALE ---
            st.success("✅ Application prête juste en dessous !")
            
            # On affiche l'appli directement ici. Elle fait 800px de haut pour bien voir.
            components.html(res_html, height=800, scrolling=True)
            
            # On laisse le bouton de secours au cas où
            st.download_button("📥 Sauvegarder le fichier (Android)", res_html, "Tournee.html", "text/html")

st.caption("Créé par Matthieu WAGNER")