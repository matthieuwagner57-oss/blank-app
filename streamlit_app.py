import streamlit as st
import pdfplumber
import re

# Configuration de la page
st.set_page_config(page_title="Scanner RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

# --- DESIGN DES ONGLETS ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f5;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 15px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1a73e8 !important; 
        color: white !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- CERVEAU DE GÉNÉRATION ---
def generate_final_app(data_input):
    cards_html = ""
    lines = data_input.strip().split('\n')
    
    for i, line in enumerate(lines):
        line_up = line.upper().strip()
        if not line_up: continue
        
        # Filtre de sécurité : on ignore les lignes sans adresses
        if not any(k in line_up for k in ["RUE", "AVENUE", "AV ", "IMP", "PL ", "SQ", "BD", "ROUTE", "CHEMIN"]):
            continue

        # Extraction Nom / Adresse / Info
        if ";" in line:
            parts = line.split(";")
            nom = parts[0].strip().upper()
            adr = parts[1].strip().upper()
            info_supp = " ".join(parts[2:]).strip().upper() if len(parts) > 2 else ""
        else:
            match = re.search(r'(\d+)', line)
            if match:
                nom = line[:match.start()].strip().upper()
                adr = line[match.start():].strip().upper()
                info_supp = ""
            else:
                nom = "CLIENT"
                adr = line.strip().upper()
                info_supp = ""

        # Détection "PAS DE JOURNAL"
        full_text = f"{nom} {adr} {info_supp}"
        is_stop = any(x in full_text for x in ["PAS DE JOURNAL", "PAS ", "SANS J", "STOP", "VACANCES", "REPOS"])
        
        color = "#ef4444" if is_stop else "#1a73e8"
        badge = '<div style="color:#ef4444; font-weight:bold; font-size:11px; margin-top:4px;">⚠️ PAS DE JOURNAL</div>' if is_stop else ""
        opacity = "0.7" if is_stop else "1"
        
        maps_url = f"https://www.google.com/maps/search/?api=1&query={adr.replace(' ','+')}"
        
        cards_html += f"""
        <div style="background:white; margin-bottom:12px; padding:15px; border-radius:15px; border-left:10px solid {color}; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 8px rgba(0,0,0,0.15); opacity:{opacity};">
            <div style="flex:1;">
                <div style="color:#1a73e8; font-weight:bold; font-size:16px;">{nom}</div>
                <div style="font-size:13px; color:#444; margin-top:4px; font-weight:bold;">{adr}</div>
                {badge}
            </div>
            <a href="{maps_url}" target="_blank" style="text-decoration:none; background:#f0f7ff; padding:12px; border-radius:12px; border:1.5px solid #1a73e8; font-size:20px;">📍</a>
        </div>"""
    
    return f"<html><body style='font-family:sans-serif; background:#f8f9fa; padding:15px;'><h2 style='color:#1a73e8;'>🗞️ MA TOURNÉE</h2>{cards_html}<p style='text-align:center; color:#999; font-size:10px; margin-top:20px;'>MATTHIEU WAGNER</p></body></html>"

# --- INTERFACE ---
st.title("🗞️ Scanner RL Pro")
st.caption("Développé par Matthieu Wagner")

# RE-CRÉATION DES 4 ONGLETS
tab1, tab2, tab3, tab4 = st.tabs(["🪄 IA", "📸 PHOTO", "📄 PDF", "🚀 GÉNÉRATEUR"])

with tab1:
    st.write("### 🧠 Extraction par IA (Claude/Gemini)")
    st.info("Meilleure méthode pour détecter les 'PAS DE JOURNAL'.")
    prompt_ia = """Analyse ce bordereau RL. 
Extrait : NOM ; ADRESSE ; INFO_LIVRAISON
- Si colonne '0' ou 'PAS' visible -> INFO_LIVRAISON = PAS DE JOURNAL
- Sinon -> INFO_LIVRAISON = (vide)
Vérifie bien l'alignement horizontal. Ne réponds que la liste."""
    st.code(prompt_ia)
    col1, col2 = st.columns(2)
    with col1: st.link_button("Ouvrir Claude", "https://claude.ai")
    with col2: st.link_button("Ouvrir Gemini", "https://gemini.google.com")

with tab2:
    st.write("### 📸 Scan Photo")
    st.file_uploader("Prendre une photo du bordereau", type=["jpg", "jpeg", "png"])
    st.warning("Utilisez le mode IA pour une meilleure précision.")

with tab3:
    st.write("### 📄 Import PDF")
    pdf_file = st.file_uploader("Choisir le PDF officiel", type="pdf")
    if pdf_file:
        st.success("Fichier prêt pour l'analyse.")

with tab4:
    st.write("### 🚀 Générateur d'Appli")
    input_data = st.text_area("Collez votre liste ici (NOM ; ADRESSE ; INFO)", height=300, placeholder="Ex: MME BOUR ; 38 RUE SAINT ANTOINE ; PAS DE JOURNAL")
    
    if st.button("📱 GÉNÉRER MA TOURNÉE MOBILE", use_container_width=True):
        if input_data:
            app_html = generate_final_app(input_data)
            st.success("✅ Application prête !")
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", app_html, "Tournee.html", "text/html")