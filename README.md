import streamlit as st
import re

# Configuration Matthieu Wagner
st.set_page_config(page_title="Système RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

# --- DESIGN DES ONGLETS ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
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

# --- GÉNÉRATEUR DU FICHIER HTML (DESIGN RITTER) ---
def generate_html_ritter(data, compact_default):
    cards_html = ""
    lines = data.strip().split('\n')
    
    for i, line in enumerate(lines):
        if ";" not in line: continue
        parts = line.split(";")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper()
        ville = parts[2].strip().upper() if len(parts) > 2 else "57600 OETING"
        info = parts[3].strip().upper() if len(parts) > 3 else ""

        # Détection d'alerte (Règle du 'N' ou 'PAS')
        is_alert = any(x in f"{nom} {info}" for x in ["PAS", " N ", "STOP", "VACANCES"])
        border_color = "#dc3545" if is_alert else "#007bff"
        alert_badge = f'<span style="color: #dc3545; font-weight: bold; background: #ffeeba; padding: 3px 6px; border-radius: 4px; border: 1px solid #ffdf7e; font-size: 14px; display: block; margin-top: 5px;">⚠️ {info}</span>' if info else ""

        cards_html += f"""
        <div class="card-container">
            <input type="checkbox" id="check_{i}" class="hidden-checkbox">
            <label class="card" for="check_{i}" style="border-left: 5px solid {border_color}">
                <div class="info-section">
                    <div style="margin-bottom: 8px;"><span class="num-badge">CLIENT : {i+1}</span></div>
                    <span class="client-name">{nom}</span>
                    <a class="maps-link" href="https://www.google.com/maps/search/?api=1&query={adr.replace(' ','+')}+{ville.replace(' ','+')}" target="_blank">📍 {adr}</a>
                    <span style="font-size: 14px; color: #555; display: block;">{ville}</span>
                    {alert_badge}
                </div>
                <div class="action-section"><div class="btn-check"></div></div>
            </label>
        </div>"""

    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #f4f4f9; padding: 10px; margin: 0; }}
        .reset-btn {{ display: block; width: 100%; padding: 12px; background: #dc3545; color: white; border: none; border-radius: 10px; margin-bottom: 10px; font-weight: bold; cursor: pointer; }}
        .compact-label {{ display: block; width: 100%; padding: 12px; background: #6c757d; color: white; border-radius: 10px; margin-bottom: 15px; font-weight: bold; text-align: center; cursor: pointer; }}
        .hidden-checkbox {{ display: none; }}
        .card {{ background: white; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: space-between; cursor: pointer; }}
        .num-badge {{ background: #333; color: white; padding: 5px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; }}
        .client-name {{ font-size: 18px; font-weight: 800; color: #111; display: block; }}
        .maps-link {{ color: #0056b3; text-decoration: none; font-weight: bold; font-size: 17px; display: inline-block; padding: 8px 0; }}
        .btn-check {{ padding: 15px; background: #007bff; color: white; border-radius: 8px; width: 85px; text-align: center; font-weight: bold; }}
        .btn-check::after {{ content: "Valider"; }}
        .hidden-checkbox:checked + .card {{ border-left-color: #28a745; background: #eafaf1; opacity: 0.6; }}
        .hidden-checkbox:checked + .card .btn-check {{ background: #28a745; }}
        .hidden-checkbox:checked + .card .btn-check::after {{ content: "✓ Fait"; }}
        
        /* MODE COMPACT */
        #compact_mode:checked ~ .card-container .card {{ padding: 6px 10px; margin-bottom: 6px; }}
        #compact_mode:checked ~ .card-container .client-name {{ font-size: 14px; }}
        #compact_mode:checked ~ .card-container .btn-check {{ padding: 8px 5px; width: 60px; font-size: 13px; }}
    </style>
</head>
<body>
    <form>
        <input type="reset" value="🔄 TOUT DÉCOCHER" class="reset-btn">
        <input type="checkbox" id="compact_mode" class="hidden-checkbox" {"checked" if compact_default else ""}>
        <label for="compact_mode" class="compact-label">🔍 Vue Compacte</label>
        <div class="card-container">{cards_html}</div>
    </form>
</body>
</html>"""

# --- INTERFACE STREAMLIT ---
st.title("🗞️ Scanner RL Pro")
st.caption("Version Design Ritter - Matthieu Wagner")

tab1, tab2, tab3, tab4 = st.tabs(["🪄 IA", "📸 PHOTO", "📄 PDF", "🚀 GÉNÉRATEUR"])

with tab1:
    st.write("### 🧠 Préparation par IA")
    st.code("Analyse ce bordereau. Format : NOM ; ADRESSE ; VILLE ; INFO. Si tu vois un 'N', écris 'PAS DE JOURNAL'.")
    st.link_button("Ouvrir Claude", "https://claude.ai")

with tab2:
    st.write("### 📸 Scan Photo")
    st.file_uploader("Importer une photo", type=["jpg", "png"])
    st.info("Utilisez le texte en direct de votre téléphone pour copier les adresses.")

with tab3:
    st.write("### 📄 Analyse PDF")
    st.file_uploader("Fichier PDF", type="pdf")

with tab4:
    st.write("### 🚀 Création de l'Appli")
    compact = st.toggle("Activer la Vue Compacte par défaut")
    data_input = st.text_area("Liste (NOM ; ADRESSE ; VILLE ; INFO)", height=300, 
                             value="MME ESTELLE BANNWART ; 16 RUE NATIONALE ; FORBACH\nM RAPHAEL AMOROSO ; 9 RUE DES VERGERS ; STIRING WENDE ; APPARTEMENT N")
    
    if st.button("📱 GÉNÉRER MA TOURNÉE", use_container_width=True):
        if data_input:
            final_html = generate_html_ritter(data_input, compact)
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", final_html, "MaTournee.html", "text/html")