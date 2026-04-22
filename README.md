import streamlit as st

st.set_page_config(page_title="Tournée RL Pro", page_icon="🗞️", layout="centered")

def generate_final_html(lines):
    cards_html = ""
    for i, line in enumerate(lines):
        if not line.strip() or ";" not in line: continue
        
        parts = line.split(";")
        nom = parts[0].strip().upper()
        adr = parts[1].strip().upper()
        consigne = parts[2].strip().upper() if len(parts) > 2 else ""
        
        is_stop = "PAS" in consigne
        color = "red" if is_stop else "#1a73e8"
        badge = f'<div style="color:red; font-weight:bold; font-size:11px;">⚠️ PAS DE JOURNAL</div>' if is_stop else ""
        
        clean_adr = adr.replace(" ", "+")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        # TECHNIQUE DU CHECKBOX INVISIBLE : Marche sans script !
        cards_html += f"""
        <div class="item">
            <input type="checkbox" id="check{i}" class="toggle">
            <label for="check{i}" class="card" style="border-left: 6px solid {color};">
                <div class="info">
                    <div class="nom">{nom}</div>
                    <div class="adr">{adr}</div>
                    {badge}
                </div>
                <div class="actions">
                    <span class="btn-v">VALIDER</span>
                    <a href="{maps_url}" target="_blank" class="btn-m" onclick="event.stopPropagation();">📍</a>
                </div>
            </label>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: sans-serif; background: #f0f2f5; padding: 10px; margin: 0; }}
            .header {{ background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #1a73e8; }}
            
            .toggle {{ display: none; }} /* On cache la case à cocher */
            
            .card {{ background: white; margin-bottom: 8px; padding: 12px; border-radius: 10px; display: flex; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.2); cursor: pointer; display: block; display: flex; justify-content: space-between; }}
            .nom {{ font-size: 14px; font-weight: bold; color: #1a73e8; }}
            .adr {{ font-size: 12px; color: #444; }}
            
            .actions {{ display: flex; align-items: center; gap: 8px; pointer-events: none; }}
            .btn-v {{ background: #eee; border: 1px solid #ccc; padding: 8px; border-radius: 6px; font-size: 10px; font-weight: bold; pointer-events: auto; }}
            .btn-m {{ text-decoration: none; border: 2px solid #1a73e8; padding: 6px 10px; border-radius: 6px; font-size: 18px; pointer-events: auto; background: white; }}
            
            /* LE SECRET : Si la case est cochée, on change le style de la carte juste après */
            .toggle:checked + .card {{ background: #d1fae5; opacity: 0.6; }}
            .toggle:checked + .card .btn-v {{ background: #22c55e; color: white; border-color: #22c55e; }}
            .toggle:checked + .card .btn-v::after {{ content: " ✅ FAIT"; }}
            .toggle:checked + .card .btn-v {{ font-size: 0; }}
            .toggle:checked + .card .btn-v::after {{ font-size: 10px; }}

            /* RESET : On recharge la page pour tout décocher */
            .btn-reset {{ background: red; color: white; border: none; padding: 8px; border-radius: 5px; font-size: 11px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <strong style="color:#1a73e8;">🗞️ MA TOURNÉE</strong>
            <button onclick="window.location.reload()" class="btn-reset">🔄 RESET</button>
        </div>
        <div id="liste">{cards_html}</div>
    </body>
    </html>
    """

st.title("🗞️ Scanner RL - Version Incassable")
data = st.text_area("Liste des clients (NOM ; ADRESSE ; OPTION) :", height=300)

if st.button("🚀 GÉNÉRER"):
    if data:
        html = generate_final_html(data.split("\n"))
        st.download_button("📥 TÉLÉCHARGER", html, "Tournee.html", "text/html")