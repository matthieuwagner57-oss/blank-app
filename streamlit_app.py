import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Scanner RL - Matthieu Wagner", page_icon="🗞️", layout="centered")

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

# --- GÉNÉRATEUR DU FICHIER HTML (DESIGN RITTER / TOURNÉE P1) ---
def generate_html_ritter(data, compact_default):
    cards_html = ""
    lines = data.strip().split('\n')
    
    for i, line in enumerate(lines):
        if ";" not in line: continue
        parts = line.split(";")
        
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper()
        ville = parts[2].strip().upper() if len(parts) > 2 else ""
        info = parts[3].strip().upper() if len(parts) > 3 else ""

        # Détection d'alerte (N ou PAS)
        is_alert = any(x in f"{nom} {info}" for x in ["PAS", " N ", "STOP", "VACANCES"])
        border_color = "#dc3545" if is_alert else "#007bff"
        alert_html = f'<span class="info-alert">⚠️ {info}</span>' if info else ""

        cards_html += f"""
        <div class="card-container">
            <input type="checkbox" id="check_{i}" class="hidden-checkbox">
            <label class="card" for="check_{i}" style="border-left-color: {border_color}">
                <div class="info-section">
                    <div class="badge-container"><span class="num-badge">ORDRE : {i+1}</span></div>
                    <span class="client-name">{nom}</span>
                    <a class="maps-link" href="https://www.google.com/maps/search/?api=1&query={adr.replace(' ','+')}+{ville.replace(' ','+')}" target="_blank" onclick="event.stopPropagation();">📍 {adr}</a>
                    <span class="city-text">{ville}</span>
                    {alert_html}
                </div>
                <div class="action-section"><div class="btn-check"></div></div>
            </label>
        </div>"""

    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>Ma Tournée RL</title>
    <style>
        body {{ font-family: -apple-system, system-ui, sans-serif; margin: 0; padding: 10px; background-color: #f4f4f9; }}
        h2 {{ text-align: center; color: #333; margin-bottom: 10px; font-size: 20px; }}
        .reset-btn {{ display: block; width: 100%; padding: 12px; background-color: #dc3545; color: white; border: none; border-radius: 10px; margin-bottom: 10px; font-size: 16px; font-weight: bold; cursor: pointer; text-align: center; }}
        .compact-label {{ display: block; width: 100%; padding: 12px; background-color: #6c757d; color: white; border: none; border-radius: 10px; margin-bottom: 15px; font-size: 16px; font-weight: bold; cursor: pointer; text-align: center; }}
        .hidden-checkbox {{ display: none; }}
        #compact_mode:checked + .compact-label {{ background-color: #343a40; }}
        .card {{ background: white; border-radius: 10px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 6px solid #007bff; display: flex; align-items: center; justify-content: space-between; cursor: pointer; }}
        .info-section {{ flex-grow: 1; }}
        .num-badge {{ background: #333; color: white; padding: 4px 8px; border-radius: 6px; font-size: 13px; font-weight: bold; display: inline-block; margin-bottom: 8px; }}
        .client-name {{ font-size: 17px; font-weight: 800; color: #111; display: block; }}
        .maps-link {{ color: #0056b3; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; padding: 8px 0; }}
        .city-text {{ font-size: 13px; color: #666; display: block; }}
        .info-alert {{ color: #dc3545; font-weight: bold; display: block; margin-top: 5px; background: #ffeeba; padding: 4px; border-radius: 4px; font-size: 13px; border: 1px solid #ffdf7e; }}
        .btn-check {{ padding: 12px; background-color: #007bff; color: white; border-radius: 8px; width: 80px; text-align: center; font-weight: bold; }}
        .btn-check::after {{ content: "Valider"; }}
        .hidden-checkbox:checked + .card {{ border-left-color: #28a745; background-color: #eafaf1; opacity: 0.6; }}
        .hidden-checkbox:checked + .card .btn-check {{ background-color: #28a745; }}
        .hidden-checkbox:checked + .card .btn-check::after {{ content: "✓ Fait"; }}

        /* MODE COMPACT */
        #compact_mode:checked ~ .card-container .card {{ padding: 8px 12px; margin-bottom: 6px; }}
        #compact_mode:checked ~ .card-container .client-name {{ font-size: 14px; }}
        #compact_mode:checked ~ .card-container .btn-check {{ padding: 8px 5px; width: 60px; font-size: 12px; }}
    </style>
</head>
<body>
    <form>
        <h2>🗞️ MA TOURNÉE</h2>
        <input type="reset" value="🔄 TOUT DÉCOCHER" class="reset-btn">
        <input type="checkbox" id="compact_mode" class="hidden-checkbox" {"checked" if compact_default else ""}>
        <label for="compact_mode" class="compact-label">🔍 Vue Compacte</label>
        <div class="card-container">
            {cards_html}
        </div>
    </form>
</body>
</html>"""

# --- INTERFACE STREAMLIT ---
st.title("🗞️ Scanner RL Pro")

tab1, tab2, tab3, tab4 = st.tabs(["🪄 IA", "📸 PHOTO", "📄 PDF", "🚀 GÉNÉRATEUR"])

with tab4:
    st.write("### 🚀 Création de l'Appli")
    compact = st.toggle("Vue Compacte par défaut")
    
    # Données par défaut pour aider
    default_text = "NOM ; ADRESSE ; VILLE ; INFO"
    
    data_input = st.text_area("Colle ta liste ici :", value=default_text, height=300)
    
    if st.button("📱 GÉNÉRER LE FICHIER MOBILE", use_container_width=True):
        if data_input and data_input != default