import streamlit as st
from openai import OpenAI
from PIL import Image
import PyPDF2
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

# --- LE PROMPT (DEMANDE UNIQUEMENT LES CARTES) ---
system_prompt = """
Tu es un robot qui extrait des adresses. Pour chaque adresse lue sur la photo, génère UNIQUEMENT le bloc HTML suivant.
INTERDICTION d'écrire <html> ou <body>. Renvoie juste la liste des <div>.

MODÈLE PAR ADRESSE :
<div class="card-wrapper">
    <input type="checkbox" id="check[ID]" class="card-input">
    <label for="check[ID]" class="card">
        <div class="card-body">
            <div class="address-text">[ADRESSE_MAJUSCULES]</div>
            <div class="special-instruction">[CONSIGNE_ROUGE_OU_VIDE]</div>
            <div class="valider-btn">Valider</div>
        </div>
        <div class="card-action">
            <a href="https://www.google.com/maps/search/?api=1&query=[ADRESSE_URL]" class="maps-btn" target="_blank" onclick="event.stopPropagation();">📍 Maps</a>
        </div>
    </label>
</div>
"""

# --- LE MOULE HTML FIXE (DESIGN RITTER 100%) ---
def generate_final_html(cards_html):
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ font-family: -apple-system, sans-serif; background-color: #f0f2f5; margin: 0; padding: 130px 15px 30px 15px; }}
        .header {{ position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 15px; text-align: center; z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-weight: bold; font-size: 18px; }}
        .top-bar {{ position: fixed; top: 55px; left: 0; width: 100%; background: white; padding: 12px; display: flex; justify-content: center; gap: 10px; z-index: 999; border-bottom: 1px solid #ddd; box-sizing: border-box; }}
        .btn-opt {{ background: #f0f2f5; border: 1px solid #ccc; padding: 8px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; cursor: pointer; color: #333; }}
        
        .card-list {{ display: flex; flex-direction: column; gap: 12px; max-width: 500px; margin: auto; }}
        .card {{ background: white; border-radius: 12px; padding: 18px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border-left: 6px solid #1a73e8; cursor: pointer; transition: 0.2s; position: relative; }}
        .address-text {{ font-size: 16px; font-weight: bold; color: #1c1e21; line-height: 1.3; }}
        .special-instruction {{ color: #d93025; font-size: 13px; font-weight: bold; margin-top: 6px; text-transform: uppercase; }}
        .valider-btn {{ margin-top: 12px; display: inline-block; padding: 5px 15px; border-radius: 15px; border: 1px solid #1a73e8; color: #1a73e8; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        
        .maps-btn {{ background: #1a73e8; color: white; padding: 12px 16px; border-radius: 10px; text-decoration: none; font-size: 14px; font-weight: bold; display: flex; align-items: center; gap: 5px; white-space: nowrap; }}
        
        /* ACTIONS CLIC */
        .card-input {{ display: none; }}
        .card-input:checked + .card {{ background: #e8eaed; border-left-color: #70757a; opacity: 0.6; transform: scale(0.98); filter: grayscale(100%); }}
        .card-input:checked + .card .address-text {{ text-decoration: line-through; color: #70757a; }}
        .card-input:checked + .card .valider-btn {{ background: #70757a; color: white; border-color: #70757a; }}
        .card-input:checked + .card .maps-btn {{ background: #70757a; }}

        /* VUE COMPACTE */
        body.compact {{ padding-top: 110px; }}
        body.compact .card {{ padding: 10px 15px; }}
        body.compact .valider-btn {{ display: none; }}
        body.compact .special-instruction {{ margin-top: 2px; font-size: 11px; }}
    </style>
</head>
<body id="mainBody">
    <div class="header">MA TOURNÉE RL</div>
    <div class="top-bar">
        <button class="btn-opt" onclick="window.location.reload()">🔄 TOUT DÉCOCHER</button>
        <button class="btn-opt" onclick="document.getElementById('mainBody').classList.toggle('compact')">🔍 VUE COMPACTE</button>
    </div>
    <div class="card-list">
        {cards_html}
    </div>
</body>
</html>
    """

def ask_ai(data, is_image=False):
    content = [{"type": "text", "text": "Extrais les adresses de ce document."}]
    if is_image:
        buffered = io.BytesIO()
        data.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}})
    else:
        content.append({"type": "text", "text": data})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": content}]
    )
    cards = re.sub(r'```html|```', '', response.choices[0].message.content).strip()
    return generate_final_html(cards)

# --- INTERFACE ---
st.title("🗞️ Tournée RL - Version Ritter")
up = st.file_uploader("Photo de la feuille :", type=["jpg", "png", "jpeg"])
if st.button("🚀 GÉNÉRER L'APPLICATION") and up:
    with st.spinner("Analyse et construction de l'app..."):
        res = ask_ai(Image.open(up), is_image=True)
        st.success("C'est prêt !")
        st.download_button("📥 TÉLÉCHARGER MON APP", res, "Tournee.html", "text/html")