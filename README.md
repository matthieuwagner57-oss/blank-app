import streamlit as st
import pdfplumber
import re

# Configuration de la page
st.set_page_config(page_title="Scanner RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

# --- FONCTION D'EXTRACTION PDF ---
def extraire_donnees_pdf(file):
    liste_propre = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    if any(k in line.upper() for k in ["RUE", "AVENUE", "IMP", "PL ", "SQ", "BD"]):
                        # Détection automatique du "N" dans le PDF
                        info_n = " ; PAS DE LIVRAISON (N)" if " N " in f" {line.upper()} " else " ; "
                        clean_line = re.sub(r'^\d{5,}\s+', '', line) # Enlève code abonné
                        liste_propre.append(f"{clean_line}{info_n}")
    return liste_propre

# --- GÉNÉRATEUR HTML FINAL ---
def generate_html(data, compact):
    cards_html = ""
    # Réglages vue compacte
    padding = "8px 12px" if compact else "15px"
    font_nom = "14px" if compact else "16px"
    margin = "6px" if compact else "12px"
    
    lines = data.strip().split('\n')
    for i, line in enumerate(lines):
        if not line.strip(): continue
        
        parts = line.split(";")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper() if len(parts) > 1 else ""
        info = parts[2].strip().upper() if len(parts) > 2 else ""

        # Détection des alertes
        is_stop = any(x in f"{nom} {adr} {info}" for x in ["PAS", " N ", "STOP", "VACANCES", "REPOS"])
        color = "#ef4444" if is_stop else "#1a73e8"
        
        cards_html += f"""
        <div class="item">
            <input type="checkbox" id="check{i}" class="toggle-done" style="display:none;">
            <label for="check{i}" class="card" style="border-left:8px solid {color}; padding:{padding}; margin-bottom:{margin};">
                <div class="info">
                    <div style="color:#1a73e8; font-weight:bold; font-size:{font_nom};">{nom}</div>
                    <div style="font-size:12px; color:#444;">{adr}</div>
                    {f'<div style="color:#ef4444; font-weight:bold; font-size:11px; margin-top:4px;">⚠️ {info}</div>' if is_stop else ""}
                </div>
                <a href="https://www.google.com/maps/search/?api=1&query={adr.replace(' ','+')}" target="_blank" class="map-btn" onclick="event.stopPropagation();">📍</a>
            </label>
        </div>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #f0f2f5; padding: 10px; margin:0; }}
            .card {{ background: white; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer; transition: 0.2s; }}
            .map-btn {{ text-decoration: none; background: #f0f7ff; padding: 10px 14px; border-radius: 10px; border: 1.5px solid #1a73e8; font-size: 20px; }}
            .toggle-done:checked + .card {{ background: #d1fae5; opacity: 0.5; border-left-color: #22c55e; }}
        </style>
    </head>
    <body>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; padding:5px;">
            <b style="color:#1a73e8; font-size:20px;">🗞️ MA TOURNÉE</b>
            <button onclick="window.location.reload()" style="background:#ef4444; color:white; border:none; padding:10px 15px; border-radius:10px; font-weight:bold; font-size:12px;">🔄 TOUT DÉCOCHER</button>
        </div>
        {cards_html}
        <div style="text-align:center; padding:20px; color:#aaa; font-size:10px; font-weight:bold;">MATTHIEU WAGNER - SYSTÈME RL</div>
    </body>
    </html>"""

# --- INTERFACE STREAMLIT ---
tab1, tab2, tab3, tab4 = st.tabs(["🪄 IA", "📸 PHOTO", "📄 PDF", "🚀 GÉNÉRATEUR"])

with tab1:
    st.write("### 🧠 Mode Expert (Claude/Gemini)")
    st.info("Copiez ce prompt pour une détection parfaite du 'N' (Pas de journal).")
    st.code("Analyse ce bordereau RL. Format : NOM ; ADRESSE ; INFO. Si tu vois un 'N' dans les jours, écris 'PAS DE JOURNAL'.")
    col1, col2 = st.columns(2)
    with col1: st.link_button("Ouvrir Claude", "https://claude.ai")
    with col2: st.link_button("Ouvrir Gemini", "https://gemini.google.com")

with tab2:
    st.write("### 📸 Scan Photo")
    photo = st.file_uploader("Prendre une photo du bordereau", type=["jpg", "jpeg", "png"])
    if photo:
        st.image(photo, caption="Aperçu pour vérification", use_container_width=True)
        if st.button("🔍 ANALYSER LA PHOTO"):
            st.info("📱 Astuce : Sur iPhone/Android, maintenez votre doigt sur le texte de l'image pour le copier directement !")

with tab3:
    st.write("### 📄 Analyse PDF")
    file_pdf = st.file_uploader("Fichier PDF officiel", type="pdf")
    if file_pdf:
        if st.button("🔍 EXTRAIRE LE TEXTE DU PDF"):
            res = extraire_donnees_pdf(file_pdf)
            if res:
                st.success(f"{len(res)} clients extraits !")
                st.text_area("Résultat à copier :", value="\n".join(res), height=250)

with tab4:
    st.write("### 🚀 Création de l'Appli")
    col_c1, col_c2 = st.columns(2)
    with col_c1: compact = st.toggle("📏 Vue Compacte", value=False)
    
    data_input = st.text_area("Collez votre liste ici :", height=300, placeholder="NOM ; ADRESSE ; INFO")
    
    if st.button("📱 GÉNÉRER L'APPLI MOBILE", use_container_width=True):
        if data_input:
            final_html = generate_html(data_input, compact)
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", final_html, "Tournee.html", "text/html")