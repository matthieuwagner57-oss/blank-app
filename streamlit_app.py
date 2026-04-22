import streamlit as st
import base64
from datetime import datetime

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

# --- JOUR ACTUEL ---
jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
nom_j = jours[datetime.now().weekday()]

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if not line.strip(): continue
        # On attend le format : NOM ; ADRESSE
        if ";" in line:
            parts = line.split(";")
            nom = parts[0].strip().upper()
            adr = parts[1].strip().upper()
        else:
            nom = "CLIENT"
            adr = line.strip().upper()
            
        clean_adr = adr.replace(" ", "+")
        # Lien Maps Direct
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        cards_html += f"""
        <div style="margin-bottom:12px; background:white; border-left:8px solid #1a73e8; padding:15px; border-radius:12px; box-shadow:0 2px 4px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center;">
            <div style="flex-grow:1;">
                <div style="font-size:16px; font-weight:900; color:#1a73e8;">{nom}</div>
                <div style="font-size:13px; font-weight:600; color:#4b5563;">{adr}</div>
                <div class="v-btn" onclick="this.innerHTML='✅ FAIT'; this.style.background='#22c55e';" style="margin-top:10px; display:inline-block; padding:5px 15px; background:#1a73e8; color:white; border-radius:15px; font-size:10px; font-weight:bold; cursor:pointer;">VALIDER LA LIVRAISON</div>
            </div>
            <a href="{maps_url}" target="_blank" style="margin-left:10px; background:white; border:2px solid #1a73e8; color:#1a73e8; padding:10px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:12px; text-align:center;">📍 MAPS</a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Ma Tournée</title>
    </head>
    <body style="font-family: -apple-system, sans-serif; background: #f4f7f9; padding: 10px; margin: 0;">
        <h2 style="color: #1a73e8; text-align: center; text-transform: uppercase;">🗞️ Tournée du {nom_j.upper()}</h2>
        {cards_html}
    </body>
    </html>
    """

st.title("🗞️ Ma Tournée RL")
st.write(f"Préparation pour **{nom_j}**")

# ZONE DE SAISIE MANUELLE (LE PLUS FIABLE)
st.subheader("📝 Liste des clients")
st.info("Colle tes adresses ci-dessous. Format : NOM ; ADRESSE")
data_input = st.text_area("Exemple : BOUR ; 38 RUE SAINT ANTOINE OETING", height=300)

if st.button("🚀 GÉNÉRER L'APPLICATION"):
    if data_input:
        lines = data_input.split("\n")
        res_html = generate_final_html(lines)
        
        st.success("✅ Application générée !")
        st.download_button("📥 TÉLÉCHARGER LE FICHIER", res_html, "Tournee.html", "text/html")
    else:
        st.warning("Ajoute au moins une adresse !")

st.divider()
st.caption("Version Démo Sécurisée - Matthieu W.")