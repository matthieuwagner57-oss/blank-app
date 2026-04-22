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
    st.error("Clé API manquante.")
    st.stop()

# --- PROMPT D'EXTRACTION ---
system_prompt = """
Tu es un robot d'extraction. Pour chaque ligne lue, génère UNIQUEMENT ce bloc HTML.
Cherche bien le NOM et l'ADRESSE. Pour Maps, utilise l'adresse.

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
            <a href="https://www.google.com/maps/search/?api=1&query=[ADRESSE_URL]" class="m-btn" target="_blank" onclick="event.stopPropagation();">📍 Maps</a>
        </div>
    </label>
</div>
"""

def generate_final_html(cards_html):
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ font-family: -apple-system, sans-serif; background-color: #f4f7f9; margin: 0; padding: 140px 15px 30px 15px; }}
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
        .cb:checked + .card {{ background: #f1f5f9; border-left-color: #22c55e; opacity: 0.8; }}
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

def ask_ai(data, is_image=False):
    content = [{"type": "text", "text": "Extrais NOMS et ADRESSES."}]
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
st.title("🗞️ Application Tournée RL")
tabs = st.tabs(["📸 Photo", "📄 PDF", "✍️ Manuel"])

with tabs[0]:
    up = st.file_uploader("Photo :", type=["jpg", "png", "jpeg"])
    if st.button("🚀 GÉNÉRER L'APPLICATION") and up:
        with st.spinner("Analyse..."):
            res_html = ask_ai(Image.open(up), is_image=True)
            
            # BOUTON POUR IPHONE (LANCE SAFARI DIRECTEMENT)
            b64 = base64.b64encode(res_html.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" target="_blank" style="padding: 15px; background: #1a73e8; color: white; text-decoration: none; border-radius: 10px; display: block; text-align: center; font-weight: bold; margin-bottom: 20px;">🚀 OUVRIR SUR IPHONE (SANS INDEED)</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            # BOUTON CLASSIQUE (POUR ANDROID)
            st.download_button("📥 Télécharger (Android/PC)", res_html, "Tournee.html", "text/html")

with tabs[2]:
    txt_in = st.text_area("Texte :")
    if st.button("🚀 GÉNÉRER (TEXTE)") and txt_in:
        res_html = ask_ai(txt_in)
        st.download_button("📥 Télécharger", res_html, "Tournee.html", "text/html")

st.divider()
st.caption("Créé par Matthieu WAGNER - Version Anti-Indeed")