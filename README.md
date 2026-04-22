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
    st.error("Erreur : Clé API manquante dans les Secrets.")
    st.stop()

# --- PROMPT D'EXTRACTION ---
system_prompt = """
Tu es un robot d'extraction d'adresses. Pour chaque ligne lue, génère UNIQUEMENT ce bloc HTML.
Pour le lien Maps, utilise l'adresse lue pour créer un lien vers Google Maps.

MODÈLE :
<div class="card-wrapper">
    <input type="checkbox" id="check[ID]" class="card-input">
    <label for="check[ID]" class="card">
        <div class="card-body">
            <div class="address-text">[ADRESSE_MAJUSCULES]</div>
            <div class="special-instruction">[CONSIGNE_OU_VIDE]</div>
            <div class="valider-btn">Valider la livraison</div>
            <div class="fait-btn">✅ FAIT</div>
        </div>
        <div class="card-action">
            <a href="https://www.google.com/maps/search/?api=1&query=[ADRESSE_URL]" class="maps-btn" target="_blank" onclick="event.stopPropagation();">📍 Maps</a>
        </div>
    </label>
</div>
"""

# --- LE MOULE HTML FINAL ---
def generate_final_html(cards_html):
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ font-family: -apple-system, sans-serif; background-color: #f4f7f9; margin: 0; padding: 140px 15px 30px 15px; }}
        .header {{ position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 15px; text-align: center; z-index: 1000; box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-weight: bold; font-size: 18px; }}
        .top-bar {{ position: fixed; top: 55px; left: 0; width: 100%; background: white; padding: 12px; display: flex; justify-content: center; gap: 10px; z-index: 999; border-bottom: 1px solid #ddd; }}
        
        .btn-reset {{ background: #fee2e2; border: 1px solid #ef4444; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #dc2626; }}
        .btn-compact {{ background: #f3f4f6; border: 1px solid #9ca3af; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #4b5563; }}
        
        .card-list {{ display: flex; flex-direction: column; gap: 15px; max-width: 500px; margin: auto; }}
        .card {{ background: white; border-radius: 15px; padding: 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 8px solid #1a73e8; cursor: pointer; transition: 0.2s; }}
        
        .address-text {{ font-size: 17px; font-weight: 800; color: #1e293b; line-height: 1.2; }}
        .special-instruction {{ color: #e11d48; font-size: 13px; font-weight: 800; margin-top: 8px; text-transform: uppercase; background: #fff1f2; padding: 4px 8px; border-radius: 4px; display: inline-block; }}
        
        .valider-btn {{ margin-top: 15px; display: inline-block; padding: 8px 20px; border-radius: 25px; background: #1a73e8; color: white; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        .fait-btn {{ display: none; margin-top: 15px; padding: 8px 20px; border-radius: 25px; background: #22c55e; color: white; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        .maps-btn {{ background: white; border: 2px solid #1a73e8; color: #1a73e8; padding: 10px 14px; border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 14px; }}
        
        .card-input {{ display: none; }}
        .card-input:checked + .card {{ background: #f1f5f9; border-left-color: #22c55e; opacity: 0.7; transform: scale(0.97); }}
        .card-input:checked + .card .address-text {{ text-decoration: line-through; color: #64748b; }}
        .card-input:checked + .card .valider-btn {{ display: none; }}
        .card-input:checked + .card .fait-btn {{ display: inline-block; }}

        body.compact .card {{ padding: 10px 15px; }}
        body.compact .valider-btn, body.compact .fait-btn {{ display: none !important; }}
    </style>
</head>
<body id="mainBody">
    <div class="header">🗞️ MA TOURNÉE RL</div>
    <div class="top-bar">
        <button class="btn-reset" onclick="document.querySelectorAll('.card-input').forEach(i=>i.checked=false)">🔄 TOUT DÉCOCHER</button>
        <button class="btn-compact" onclick="document.body.classList.toggle('compact')">🔍 VUE COMPACTE</button>
    </div>
    <div class="card-list">{cards_html}</div>
</body>
</html>
    """

def ask_ai(data, is_image=False):
    content = [{"type": "text", "text": "Extrais les adresses pour mon application de livraison."}]
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

# --- INTERFACE STREAMLIT ---
st.title("🗞️ Application Tournée RL")

tabs = st.tabs(["📸 Photo", "📄 Fichier PDF", "✍️ Texte Manuel"])

with tabs[0]:
    up_img = st.file_uploader("Prendre une photo :", type=["jpg", "png", "jpeg"])
    if st.button("🚀 GÉNÉRER DEPUIS PHOTO") and up_img:
        with st.spinner("Analyse de l'image..."):
            res = ask_ai(Image.open(up_img), is_image=True)
            st.download_button("📥 TÉLÉCHARGER MON APP", res, "Tournee.html", "text/html")

with tabs[1]:
    up_file = st.file_uploader("Uploader un PDF :", type=["pdf"])
    if st.button("🚀 GÉNÉRER DEPUIS PDF") and up_file:
        with st.spinner("Lecture du PDF..."):
            pdf_reader = PyPDF2.PdfReader(up_file)
            txt = "".join([page.extract_text() for page in pdf_reader.pages])
            res = ask_ai(txt)
            st.download_button("📥 TÉLÉCHARGER MON APP", res, "Tournee.html", "text/html")

with tabs[2]:
    txt_input = st.text_area("Coller les adresses ici :")
    if st.button("🚀 GÉNÉRER DEPUIS TEXTE") and txt_input:
        with st.spinner("Traitement du texte..."):
            res = ask_ai(txt_input)
            st.download_button("📥 TÉLÉCHARGER MON APP", res, "Tournee.html", "text/html")

st.divider()
st.caption("Créé par Matthieu WAGNER - Version RL Pro Interactive")