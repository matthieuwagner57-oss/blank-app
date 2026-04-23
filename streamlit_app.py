import streamlit as st
import re

# Configuration de la page pour un look pro
st.set_page_config(page_title="Système RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

# --- STYLE CSS POUR LES ONGLETS ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f5;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1a73e8 !important; 
        color: white !important; 
    }
    </style>
""", unsafe_allow_html=True)

def generate_final_app(data_input):
    """Génère le fichier HTML mobile avec suivi de livraison"""
    cards_html = ""
    lines = data_input.strip().split('\n')
    
    for i, line in enumerate(lines):
        if not line.strip(): continue
        
        # LOGIQUE D'EXTRACTION AUTOMATIQUE
        # Si l'utilisateur met un ";", on l'utilise. Sinon, on cherche l'adresse.
        if ";" in line:
            parts = line.split(";")
            nom = parts[0].strip().upper()
            adr = parts[1].strip().upper()
        else:
            # On cherche les mots-clés de rue pour séparer le nom de l'adresse
            match = re.search(r"( RUE| AV| IMP| PL| SQ| BD| ROUTE| CHEMIN)", line, re.IGNORECASE)
            if match:
                nom = line[:match.start()].strip().upper()
                adr = line[match.start():].strip().upper()
            else:
                nom = "CLIENT"
                adr = line.strip().upper()

        # Détection des arrêts (Marquage en rouge)
        is_stop = any(x in nom for x in ["BOUR", "REB", "ARRÊT", "PAS"])
        color = "#ef4444" if is_stop else "#1a73e8"
        badge = '<div style="color:#ef4444; font-weight:bold; font-size:11px; margin-top:4px;">⚠️ PAS DE JOURNAL</div>' if is_stop else ""
        
        # Lien Google Maps
        maps_url = f"https://www.google.com/maps/search/?api=1&query={adr.replace(' ','+')}"
        
        cards_html += f"""
        <div class="card" style="background:white; margin-bottom:12px; padding:15px; border-radius:15px; border-left:10px solid {color}; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 8px rgba(0,0,0,0.15);">
            <div style="flex:1;">
                <div style="color:#1a73e8; font-weight:bold; font-size:16px; letter-spacing:0.5px;">{nom}</div>
                <div style="font-size:13px; color:#444; margin-top:4px; font-weight:500;">{adr}</div>
                {badge}
            </div>
            <a href="{maps_url}" target="_blank" style="text-decoration:none; background:#f0f7ff; padding:12px; border-radius:12px; border:1.5px solid #1a73e8; font-size:20px;">📍</a>
        </div>"""
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #f8f9fa; padding: 15px; margin: 0; }}
            .header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }}
            .footer {{ text-align:center; color:#999; font-size:12px; margin-top:30px; font-weight:bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <b style="color:#1a73e8; font-size:22px;">🗞️ MA TOURNÉE</b>
            <button onclick="window.location.reload()" style="background:#ef4444; color:white; border:none; padding:8px 15px; border-radius:8px; font-weight:bold;">🔄 RESET</button>
        </div>
        {cards_html}
        <div class="footer">DÉVELOPPÉ PAR MATTHIEU WAGNER</div>
    </body>
    </html>
    """

# --- INTERFACE PRINCIPALE ---
st.title("🗞️ Scanner de Tournée RL")
st.markdown("### 👨‍💻 Créé par Matthieu Wagner")

# Les onglets demandés
tab1, tab2, tab3 = st.tabs(["✍️ MODE MANUEL", "📸 PHOTO IA", "📄 PDF IA"])

with tab1:
    st.write("### 📝 Saisie ou Collage")
    st.info("Collez votre liste ici. Format conseillé : **NOM ; ADRESSE**")
    
    # Liste d'exemple (Oeting)
    demo_list = "BERNADETTE BOUR ; 38 RUE SAINT ANTOINE\nROLAND GREFF ; 55 RUE SAINT ANTOINE\nARLETTE ROSAR ; 79 RUE SAINT ANTOINE"
    
    user_input = st.text_area("Données de la tournée :", value=demo_list, height=350)
    
    if st.button("🚀 GÉNÉRER L'APPLICATION", use_container_width=True):
        if user_input:
            app_html = generate_final_app(user_input)
            st.success("✅ Application créée avec succès !")
            st.download_button("📥 TÉLÉCHARGER POUR MOBILE", app_html, "MaTournee.html", "text/html")

with tab2:
    st.write("### 📸 Extraction via Photo")
    st.write("Prenez une photo nette du bordereau de livraison.")
    img = st.file_uploader("Capturez ou importez une image", type=["jpg", "png", "jpeg"])
    if img:
        st.warning("⚠️ L'analyse visuelle directe nécessite une clé API. Utilisez le copier-coller du texte pour l'instant.")

with tab3:
    st.write("### 📄 Extraction via PDF")
    st.write("Importez le fichier PDF officiel du Républicain Lorrain.")
    pdf = st.file_uploader("Choisir le fichier PDF", type="pdf")
    if pdf:
        st.warning("⚠️ L'analyse directe du PDF est en cours de développement. Copiez le texte du PDF dans le mode manuel.")

st.markdown("---")
st.caption("Système optimisé pour smartphone - Version 2.0")