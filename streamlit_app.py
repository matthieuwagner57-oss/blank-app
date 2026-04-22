import streamlit as st
import re

st.set_page_config(page_title="Système RL - Matthieu Wagner", page_icon="🗞️")

# --- FONCTION DE NETTOYAGE (LE CERVEAU) ---
def extraire_proprement(texte_vrac):
    lines = texte_vrac.split('\n')
    resultats = []
    # Mots-clés pour repérer une adresse
    keywords = ["RUE", "AVENUE", "IMP", "IMPASSE", "SQ", "SQUARE", "PL ", "PLACE", "BD ", "ROUTE"]
    
    for line in lines:
        line = line.strip().upper()
        if any(k in line for k in keywords):
            # 1. Nettoyage des numéros de client en début de ligne (ex: 0259401)
            line = re.sub(r'^\d{4,}\s+', '', line)
            
            # 2. Séparation Nom / Adresse
            found = False
            for k in keywords:
                if k in line:
                    parts = line.split(k, 1)
                    nom = parts[0].strip(", ").strip()
                    adr = k + parts[1].strip()
                    if not nom: nom = "CLIENT"
                    resultats.append(f"{nom} ; {adr}")
                    found = True
                    break
    return "\n".join(resultats)

# --- MENU NAVIGATION ---
rubrique = st.sidebar.radio("Navigation", ["📂 Extracteur d'adresses", "🚀 Générateur d'Appli"])

# --- RUBRIQUE 1 : EXTRACTEUR ---
if rubrique == "📂 Extracteur d'adresses":
    st.title("📂 Extracteur Magique")
    st.write("### Transformez une capture d'écran en liste propre")
    st.info("Collez ici le texte brut issu de votre screenshot. L'outil va extraire uniquement les noms et adresses.")
    
    texte_brut = st.text_area("📋 Collez le vrac ici :", height=300, placeholder="Ex: 0259401 BOUR BERNADETTE 38 RUE SAINT ANTOINE...")
    
    if st.button("🪄 NETTOYER LA LISTE"):
        if texte_brut:
            liste_propre = extraire_proprement(texte_brut)
            st.success("✅ Extraction réussie ! Copiez la liste ci-dessous :")
            st.code(liste_propre, language="text")
            st.caption("💡 Copiez ce texte et allez dans l'onglet 'Générateur d'Appli'")

# --- RUBRIQUE 2 : GÉNÉRATEUR ---
else:
    st.title("🚀 Générateur d'Appli Mobile")
    st.write("### Créez votre fichier de tournée")
    
    liste_input = st.text_area("📋 Collez la liste propre (NOM ; ADRESSE) :", height=300)
    
    if st.button("📱 CRÉER MON APPLI"):
        if ";" in liste_input:
            # Code HTML de l'appli (on garde ton design avec les cases à cocher)
            cards_html = ""
            for i, line in enumerate(liste_input.split('\n')):
                if ";" in line:
                    n, a = line.split(";", 1)
                    is_stop = any(x in n.upper() for x in ["BOUR", "REB"])
                    color = "red" if is_stop else "#1a73e8"
                    cards_html += f"""
                    <div style="background:white; margin-bottom:8px; padding:12px; border-radius:10px; border-left:8px solid {color}; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                        <div><b>{n}</b><br><small>{a}</small></div>
                        <a href="https://www.google.com/maps/search/?api=1&query={a.replace(' ','+')}" target="_blank" style="text-decoration:none; font-size:20px;">📍</a>
                    </div>"""
            
            full_html = f"<html><body style='font-family:sans-serif; background:#f0f2f5; padding:10px;'>{cards_html}<p style='text-align:center; font-size:10px;'>Créé par Matthieu Wagner</p></body></html>"
            st.download_button("📥 TÉLÉCHARGER", full_html, "MaTournee.html")
        else:
            st.error("Format invalide. Utilisez l'Extracteur d'abord !")

st.sidebar.markdown("---")
st.sidebar.write("🛠️ **Développeur :**")
st.sidebar.write("Matthieu Wagner")