import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from PIL import Image
import base64
import io
import re

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="wide")

# --- CONNEXION ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("Clé API manquante.")
    st.stop()

# --- PROMPT ---
system_prompt = """
Tu es un robot d'extraction. Pour chaque adresse, génère ce bloc. 
Remplace [NOM] et [ADRESSE] par les infos lues.

MODÈLE :
<div class="item">
    <input type="checkbox" id="c[ID]" class="cb">
    <label for="c[ID]" class="card">
        <div class="c-body">
            <div class="nom-client">[NOM]</div>
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
        body {{ font-family: -apple-system, sans-serif; background: #f4f7f9; margin: 0; padding: 110px 10px 20px 10px; }}
        .header {{ position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 12px; text-align: center; z-index: 1000; font-weight: bold; font-size: 16px; }}
        .top-bar {{ position: fixed; top: 45px; left: 0; width: 100%; background: white; padding: 10px; display: flex; justify-content: center; gap: 10px; z-index: 999; border-bottom: 1px solid #ddd; }}
        .btn-r {{ background: #fee2e2; border: 1px solid #ef4444; padding: 8px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; color: #dc2626; }}
        .btn-c {{ background: #f3f4f6; border: 1px solid #9ca3af; padding: 8px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; color: #4b5563; }}
        #compact-toggle {{ display: none; }}
        #compact-toggle:checked ~ form .card {{ padding: 8px 12px; }}
        #compact-toggle:checked ~ form .v-btn, #compact-toggle:checked ~ form .f-btn {{ display: none !important; }}
        .list {{ display: flex; flex-direction: column; gap: 10px; max-width: 500px; margin: auto; }}
        .card {{ background: white; border-radius: 12px; padding: 15px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 6px solid #1a73e8; }}
        .nom-client {{ font-size: 16px; font-weight: 800; color: #1a73e8; text-transform: uppercase; }}
        .adr {{ font-size: 14px; color: #4b5563; }}
        .v-btn {{ margin-top: 10px; display: inline-block; padding: 6px 15px; border-radius: 20px; background: #1a73e8; color: white; font-size: 11px; font-weight: bold; }}
        .f-btn {{ display: none; margin-top: 10px; padding: 6px 15px; border-radius: 20px; background: #22c55e; color: white; font-size: 11px; font-weight: bold; }}
        .m-btn {{ background: white; border: 1px solid #1a73e8; color: #1a73e8; padding: 8px 12px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 13px; }}
        .cb {{ display: none; }}
        .cb:checked + .card {{ background: #f1f5f9; border-left-color: #22c55e; opacity: 0.7; }}
        .cb:checked + .card .v-btn {{ display: none; }}
        .cb:checked + .card .f-btn {{ display: inline-block; }}
        .cb:checked + .card .nom-client, .cb:checked + .card .adr {{ text-decoration: line-through; color: #94a3b8; }}
    </style>
</head>
<body>
    <input type="checkbox" id="compact-toggle">
    <div class="header">🗞️ MA TOURNÉE</div>
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
st.title("🗞️ Scanner de Tournée")

up = st.file_uploader("Photo de la feuille :", type=["jpg", "png", "jpeg"])

if up:
    if st.button("🚀 GÉNÉRER L'APPLI MAINTENANT"):
        with st.spinner("Lecture des adresses..."):
            res_html = ask_ai(Image.open(up))
            
            st.success("✅ Terminée ! Voici ta liste :")
            
            # MAGIE : On affiche l'application directement dans la page Streamlit
            # On ajuste la hauteur pour que ce soit confortable sur mobile
            components.html(res_html, height=600, scrolling=True)
            
            st.divider()
            st.info("Tu peux utiliser la liste directement ci-dessus ! Si tu veux l'enregistrer, utilise le bouton ci-dessous.")
            st.download_button("📥 Télécharger le fichier", res_html, "Tournee.html", "text/html")

st.caption("Créé par Matthieu WAGNER")