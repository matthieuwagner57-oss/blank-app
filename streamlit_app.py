import streamlit as st
import re

# Configuration de la page
st.set_page_config(page_title="Système RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
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

# --- LOGIQUE DE GÉNÉRATION ---
def generate_html_app(data):
    cards_html = ""
    lines = data.strip().split('\n')
    for i, line in enumerate(lines):
        if ";" not in line: continue
        parts = line.split(";")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper()
        
        # Alerte si l'IA n'est pas sûre ou si c'est un arrêt
        is_warning = any(x in nom for x in ["BOUR", "REB", "[?]"])
        color = "#ef4444" if is_warning else "#1a73e8"
        
        maps_url = f"https://www.google.com/maps/search/?api=1&query={adr.replace(' ','+')}"
        
        cards_html += f"""
        <div style="background:white; margin-bottom:12px; padding:15px; border-radius:15px; border-left:10px solid {color}; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
            <div style="flex:1;">
                <div style="color:#1a73e8; font-weight:bold; font-size:16px;">{nom}</div>
                <div style="font-size:13px; color:#444; margin-top:4px;">{adr}</div>
            </div>
            <a href="{maps_url}" target="_blank" style="text-decoration:none; background:#f0f7ff; padding:12px; border-radius:12px; border:1.5px solid #1a73e8; font-size:20px;">📍</a>
        </div>"""
        
    return f"<html><body style='font-family:sans-serif; background:#f8f9fa; padding:15px;'>{cards_html}<p style='text-align:center; color:#999; font-size:10px;'>MATTHIEU WAGNER - SYSTÈME RL</p></body></html>"

# --- INTERFACE ---
st.title("🗞️ Scanner de Tournée RL")
st.caption("Solution développée par Matthieu Wagner")

# LES 3 CHOIX POUR L'UTILISATEUR
tab1, tab2, tab3 = st.tabs(["🪄 EXTRACTEUR IA (Conseillé)", "📸 PHOTO / PDF DIRECT", "🚀 GÉNÉRATEUR"])

with tab1:
    st.write("### 🪄 Méthode Haute Précision")
    st.info("Utilisez la puissance de vision de Claude ou Gemini pour déchiffrer votre bordereau sans erreur.")
    
    prompt = """Analyse ce bordereau RL. 
Extrait CHAQUE client sous ce format exact :
NOM ; NUMÉRO ET RUE ; VILLE

Règles :
1. Ignore les codes abonnés et les dates.
2. Si une info manque, mets [?].
3. Ne réponds que la liste."""

    st.markdown("**1. Copiez le prompt spécial :**")
    st.code(prompt)
    
    st.markdown("**2. Envoyez votre photo à l'IA :**")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🤖 Claude.ai (Recommandé)", "https://claude.ai")
    with col2:
        st.link_button("♊ Gemini Google", "https://gemini.google.com")
    
    st.divider()
    st.caption("Une fois la liste obtenue, copiez-la et allez dans l'onglet 'GÉNÉRATEUR'.")

with tab2:
    st.write("### 📥 Importation Directe")
    st.write("Si vous préférez essayer l'analyse interne (en test) :")
    
    option = st.radio("Type de fichier :", ["Photo du bordereau", "Fichier PDF officiel"])
    
    if option == "Photo du bordereau":
        st.file_uploader("Prendre une photo", type=["jpg", "jpeg", "png"])
    else:
        st.file_uploader("Choisir le PDF", type="pdf")
        
    if st.button("Lancer l'analyse directe"):
        st.warning("⚠️ L'analyse directe est moins précise que la méthode IA (onglet 1).")

with tab3:
    st.write("### 📱 Création de l'Appli")
    st.write("Collez ici votre liste finale pour fabriquer votre outil de livraison.")
    
    input_data = st.text_area("Liste au format NOM ; ADRESSE", height=300, placeholder="Ex: MME BOUR ; 38 RUE SAINT ANTOINE")
    
    if st.button("GÉNÉRER MON APPLI MOBILE", use_container_width=True):
        if ";" in input_data:
            app_html = generate_html_app(input_data)
            st.success("✅ Application générée !")
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", app_html, "MaTournee.html", "text/html")
        else:
            st.error("Format invalide. Utilisez 'NOM ; ADRESSE'")

st.markdown("---")
st.caption("Matthieu Wagner - Centre de Commande Tournée v2.5")