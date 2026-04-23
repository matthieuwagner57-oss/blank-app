import streamlit as st
import re

st.set_page_config(page_title="Scanner RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

# --- CERVEAU DE L'APPLI ---
def generate_final_html(data):
    cards_html = ""
    lines = data.strip().split('\n')
    for i, line in enumerate(lines):
        if ";" not in line: continue
        n, a = line.split(";", 1)
        nom = n.strip().upper()
        adr = a.strip().upper()
        is_stop = any(x in nom for x in ["BOUR", "REB", "[?]"])
        color = "#ef4444" if is_stop else "#1a73e8"
        
        cards_html += f"""
        <div style="background:white; margin-bottom:10px; padding:15px; border-radius:12px; border-left:8px solid {color}; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <div style="flex:1;">
                <div style="color:#1a73e8; font-weight:bold; font-size:15px;">{nom}</div>
                <div style="font-size:13px; color:#333; margin-top:3px;">{adr}</div>
            </div>
            <a href="https://www.google.com/maps/search/?api=1&query={adr.replace(' ','+')}" target="_blank" style="text-decoration:none; padding:10px; font-size:20px;">📍</a>
        </div>"""
    return f"<html><body style='font-family:sans-serif; background:#f8f9fa; padding:10px;'>{cards_html}</body></html>"

# --- INTERFACE ---
st.title("🗞️ Centre de Commande RL")
st.caption("Développé par Matthieu Wagner")

# NAVIGATION PAR ONGLETS
tab1, tab2 = st.tabs(["🚀 GÉNÉRATEUR", "🪄 EXTRACTEUR IA"])

with tab2:
    st.write("### 🪄 Étape 1 : Extraire avec l'IA")
    st.info("Puisque Claude et Gemini lisent mieux les photos, utilisez-les pour préparer la liste.")
    
    prompt_complet = """Analyse ce bordereau RL. 
Extrait CHAQUE client sous ce format exact :
NOM ; NUMÉRO ET RUE ; VILLE

Règles :
1. Ignore les codes abonnés et les dates.
2. Si une info manque, mets [?].
3. Ne dis rien d'autre que la liste."""

    st.markdown("**1. Copiez ce prompt :**")
    st.code(prompt_complet)
    
    st.markdown("**2. Ouvrez l'IA de votre choix :**")
    col_a, col_b = st.columns(2)
    with col_a:
        st.link_button("🤖 Ouvrir Claude (Top pour les PDF)", "https://claude.ai")
    with col_b:
        st.link_button("♊ Ouvrir Gemini (Top sur Android)", "https://gemini.google.com")
        
    st.write("---")
    st.write("👉 *Une fois que l'IA vous a répondu, copiez la liste et allez dans l'onglet 'Générateur'.*")

with tab1:
    st.write("### 🚀 Étape 2 : Créer l'Application")
    user_list = st.text_area("Collez la liste obtenue ici :", height=300, placeholder="NOM ; ADRESSE")
    
    if st.button("📱 GÉNÉRER MA TOURNÉE", use_container_width=True):
        if ";" in user_list:
            html = generate_final_html(user_list)
            st.success("✅ Application prête !")
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", html, "MaTournee.html", "text/html")
        else:
            st.error("Le format doit être : NOM ; ADRESSE")