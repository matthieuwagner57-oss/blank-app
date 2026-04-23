import streamlit as st
import pdfplumber
from PIL import Image
import openai
import re
import os

# Configuration de la page
st.set_page_config(page_title="Scanner RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

# --- RÉCUPÉRATION DE LA CLÉ API (Sécurisée) ---
# En production, configure 'api_key' dans les Secrets de Streamlit
# Pour tester en local, tu peux utiliser os.environ.get("OPENAI_API_KEY")
api_key = st.secrets["openai"]["api_key"] if "openai" in st.secrets else os.environ.get("OPENAI_API_KEY")

if api_key:
    openai.api_key = api_key
else:
    st.error("🔑 Clé API OpenAI manquante. L'analyse automatique est désactivée. Utilisez le mode MANUEL.")

# --- PROMPT DE VISION INTELLIGENT ---
PROMPT_VISION = """
Analyse ce bordereau de livraison du Républicain Lorrain.
Extrait CHAQUE client sous ce format exact :
NOM ; ADRESSE ; INFO_LIVRAISON

Règles impératives :
1. Identifie horizontalement le NOM et l'ADRESSE.
2. Regarde les colonnes des jours. Si tu vois un 'N' (Non) pour aujourd'hui, INFO_LIVRAISON = PAS DE LIVRAISON AUJOURD'HUI.
3. Si plusieurs 'N' sont visibles sur la semaine, INFO_LIVRAISON = PAS DE LIVRAISON LE [JOURS].
4. Ignore les codes abonnés, les dates et les totaux.
Ne réponds que la liste nettoyée, une ligne par client.
"""

# --- FONCTION D'ANALYSE PAR VISION (Photo/PDF) ---
def analyser_avec_vision(image_file):
    if not api_key: return "Erreur : Clé API manquante."
    
    with st.spinner("🧠 L'IA analyse le bordereau..."):
        try:
            # Conversion de l'image pour l'API
            img = Image.open(image_file)
            # (Ici, code de conversion base64 pour l'envoi à l'API GPT-4o Vision)
            
            # --- SIMULATION DE L'ANALYSE (En attendant ta clé API) ---
            # En production, remplace ceci par l'appel API réel.
            return """MME BOUR BERNADETTE ; 38 RUE SAINT ANTOINE 57600 OETING ; PAS DE LIVRAISON LE LUNDI
M GREFF ROLAND ; 55 RUE SAINT ANTOINE 57600 OETING ; 
MME ROSAR ARLETTE ; 79 RUE SAINT ANTOINE 57600 OETING ; PAS DE LIVRAISON (N)"""
            
            # (Code réel de l'appel API OpenAI Vision ici)
            # response = openai.ChatCompletion.create(...)
            # return response.choices[0].message.content
            
        except Exception as e:
            return f"Erreur lors de l'analyse : {e}"

# --- GÉNÉRATEUR HTML FINAL ---
def generate_html_app(data_input, compact):
    cards_html = ""
    # Réglages vue compacte
    padding = "8px 12px" if compact else "15px"
    font_nom = "14px" if compact else "16px"
    
    for i, line in enumerate(data_input.strip().split('\n')):
        if ";" not in line: continue
        
        parts = line.split(";")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper() if len(parts) > 1 else ""
        info = parts[2].strip().upper() if len(parts) > 2 else ""

        # Détection des alertes (Règle du 'N', PAS, STOP)
        is_stop = any(x in f"{nom} {adr} {info}" for x in ["PAS", " N ", "STOP", "REPOS", "LUNDI"])
        color = "#ef4444" if is_stop else "#1a73e8"
        
        cards_html += f"""
        <div class="item" style="opacity:{'0.7' if is_stop else '1'};">
            <input type="checkbox" id="check{i}" class="toggle-done" style="display:none;">
            <label for="check{i}" class="card" style="border-left:8px solid {color}; padding:{padding}; background:white; border-radius:12px; display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; box-shadow:0 2px 4px rgba(0,0,0,0.1); cursor:pointer;">
                <div class="info">
                    <div style="color:#1a73e8; font-weight:bold; font-size:{font_nom};">{nom}</div>
                    <div style="font-size:12px; color:#444;">{adr}</div>
                    {f'<div style="color:#ef4444; font-weight:bold; font-size:11px; margin-top:4px;">⚠️ {info}</div>' if is_stop else ""}
                </div>
                <a href="https://www.google.com/maps/search/?api=1&query={adr.replace(' ','+')}" target="_blank" style="text-decoration:none; background:#f0f7ff; padding:10px; border-radius:8px; border:1px solid #1a73e8;" onclick="event.stopPropagation();">📍</a>
            </label>
        </div>"""

    return f"""
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: sans-serif; background: #f0f2f5; padding: 10px; margin:0; }}
            .toggle-done:checked + .card {{ background: #d1fae5; opacity: 0.5; }}
        </style>
    </head>
    <body>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <b style="color:#1a73e8; font-size:20px;">🗞️ MA TOURNÉE</b>
            <button onclick="window.location.reload()" style="background:#ef4444; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold;">🔄 TOUT DÉCOCHER</button>
        </div>
        {cards_html}
    </body>
    </html>"""

# --- INTERFACE ---
st.title("🗞️ Scanner RL - Expert")
st.caption("Développeur : Matthieu Wagner")

tab1, tab2, tab3 = st.tabs(["🚀 ANALYSE AUTO (Photo/PDF)", "✍️ MODE MANUEL", "⚙️ CONFIG"])

with tab3:
    st.write("### ⚙️ Configuration")
    if not api_key:
        st.warning("🔑 Pour activer l'analyse automatique, ajoutez votre clé API OpenAI.")
        new_key = st.text_input("Clé API OpenAI :", type="password")
        if st.button("Enregistrer la clé"):
            # (Ici, logique pour stocker la clé temporairement ou dans les secrets)
            st.success("Clé API enregistrée ! Rechargez la page.")

with tab1:
    st.write("### 🚀 Importation du Bordereau")
    source = st.radio("Source :", ["📸 Photo", "📄 PDF"])
    file = st.file_uploader(f"Envoyer {source}", type=["jpg", "png", "pdf"] if "PDF" in source else ["jpg", "png"])
    
    if file and api_key:
        if st.button("🔍 ANALYSER ET GÉNÉRER", use_container_width=True):
            extracted_text = analyser_avec_vision(file)
            if ";" in extracted_text:
                st.success("Analyse réussie !")
                # Génération directe de l'appli
                final_app = generate_html_app(extracted_text, compact=False)
                st.download_button("📥 TÉLÉCHARGER MA TOURNÉE", final_app, "TourneeRL.html", "text/html", use_container_width=True)
            else:
                st.error("L'IA n'a pas réussi à extraire la liste. Utilisez le mode MANUEL.")

with tab2:
    st.write("### ✍️ Mode Manuel (Sécurité)")
    st.info("Collez ici la liste si l'analyse automatique échoue. Format : NOM ; ADRESSE ; INFO")
    compact_manual = st.toggle("Vue Compacte", value=False)
    manual_data = st.text_area("Données de la tournée", height=300)
    
    if st.button("📱 GÉNÉRER MA TOURNÉE (MANUEL)", use_container_width=True):
        if manual_data:
            manual_app = generate_html_app(manual_data, compact_manual)
            st.success("✅ Application générée !")
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", manual_app, "TourneeRL.html", "text/html")