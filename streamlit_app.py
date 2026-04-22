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
Extrais bien le NOM et l'ADRESSE.

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
            <a href="https://www.google.com/maps/search/[ADRESSE_URL]" class="m-btn" target="_blank" onclick="event.stopPropagation();">📍 Maps</a>
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
        body {{ font-family: -apple-system, sans-serif; background: #f4f7f9; margin: 0; padding: 140px 15px 30px 15px; }}
        .header {{ position: fixed; top: 0; left: 0; width: 100%; background: #1a73e8; color: white; padding: 15px; text-align: center; z-index: 1000; font-weight: bold; }}
        .top-bar {{ position: fixed; top: 50px; left: 0; width: 100%; background: white; padding: 12px; display: flex; justify-content: center; gap: 10px; z-index: 999; border-bottom: 1px solid #ddd; }}
        .btn-r {{ background: #fee2e2; border: 1px solid #ef4444; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #dc2626; }}
        .btn-c {{ background: #f3f4f6; border: 1px solid #9ca3af; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #4b5563; }}
        #compact-toggle {{ display: none; }}
        #compact-toggle:checked ~ form .card {{ padding: 10px 15px; }}
        #compact-toggle:checked ~ form .v-btn, #compact-toggle:checked ~ form .f-btn {{ display: none !important; }}
        .list {{ display: flex; flex-direction: column; gap: 15px; max-width: 500px; margin: auto; }}
        .card {{ background: white; border-radius: 15px; padding: 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 8px solid #1a73e8; }}
        .nom-client {{ font-size: 18px; font-weight: 900; color: #1a73e8; text-transform: uppercase; }}
        .adr {{ font-size: 15px; font-weight: 600; color: #4b5563; }}
        .v-btn {{ margin-top: 15px; display: inline-block; padding: 8px 20px; border-radius: 25px; background: #1a73e8; color: white; font-size: 12px; font-weight: bold; }}
        .f-btn {{ display: none; margin-top: 15px; padding: 8px 20px; border-radius: 25px; background: #22c55e; color: white; font-size: 12px; font-weight: bold; }}
        .m-btn {{ background: white; border: 2px solid #1a73e8; color: #1a73e8; padding: 10px 14px; border-radius: 12px; text-decoration: none; font-weight: bold; }}
        .cb {{ display: none; }}
        .cb:checked + .card {{ background: #f1f5f9; border-left-color: #22c55e; opacity: 0.8; }}
        .cb:checked + .card .v-btn {{ display: none; }}
        .cb:checked + .card .f-btn {{ display: inline-block; }}
        .cb:checked + .card .nom-client, .cb:checked + .card .adr {{ text-decoration: line-through; color: #94a3b8; }}
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

up = st.file_uploader("Photo :", type=["jpg", "png", "jpeg"])

if st.button("🚀 GÉNÉRER L'APPLICATION") and up:
    with st.spinner("Analyse en cours..."):
        res_html = ask_ai(Image.open(up), is_image=True)
        
        # --- SOLUTION ANTI-PAGE BLANCHE IPHONE ---
        # Au lieu d'un lien direct, on crée un petit bouton de secours
        b64 = base64.b64encode(res_html.encode('utf-8')).decode('utf-8')
        
        st.success("✅ Application prête !")
        
        # Bouton 1 : Pour Android/PC (Téléchargement)
        st.download_button("📥 Télécharger pour Android", res_html, "Tournee.html", "text/html")
        
        st.divider()
        st.subheader("📱 Version iPhone")
        st.info("Sur iPhone, reste appuyé sur le bouton bleu et choisis 'Ouvrir dans Safari' ou clique simplement dessus.")
        
        # Le lien est maintenant "propre" pour Safari
        data_url = f"data:text/html;charset=utf-8;base64,{b64}"
        st.markdown(f'''
            <a href="{data_url}" target="_self" style="display: block; text-align: center; padding: 20px; background-color: #1a73e8; color: white; text-decoration: none; border-radius: 15px; font-weight: bold; font-size: 18px;">
                🚀 OUVRIR SUR IPHONE
            </a>
            ''', unsafe_allow_html=True)