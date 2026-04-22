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
        
        # Détection de l'arrêt
        is_stop = "PAS" in consigne
        badge = f'<div class="badge-stop">⚠️ PAS DE JOURNAL LE LUNDI</div>' if is_stop else ""
        border_color = "#ef4444" if is_stop else "#1a73e8"
        
        clean_adr = adr.replace(" ", "+")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        cards_html += f"""
        <div class="card" id="card{i}" style="border-left: 6px solid {border_color};">
            <div class="card-info">
                <div class="client-nom">{nom}</div>
                <div class="client-adr">{adr}</div>
                {badge}
            </div>
            <div class="card-actions">
                <button onclick="markDone({i})" id="btn{i}" class="btn-valider">VALIDER</button>
                <a href="{maps_url}" target="_blank" class="btn-maps">📍</a>
            </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #f0f2f5; padding: 10px; margin: 0; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; position: sticky; top: 0; background: #f0f2f5; padding: 5px 0; z-index: 100; }}
            
            /* Styles des Cartes */
            .card {{ background: white; margin-bottom: 8px; padding: 12px 15px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; transition: 0.2s; }}
            .client-nom {{ font-size: 15px; font-weight: 800; color: #1a73e8; line-height: 1.2; }}
            .client-adr {{ font-size: 13px; font-weight: 600; color: #4b5563; }}
            .badge-stop {{ color: #ef4444; font-weight: bold; font-size: 11px; margin-top: 4px; }}
            
            /* Boutons */
            .card-actions {{ display: flex; align-items: center; gap: 8px; }}
            .btn-valider {{ background: #f3f4f6; border: 1px solid #d1d5db; color: #374151; padding: 10px 14px; border-radius: 8px; font-size: 11px; font-weight: bold; cursor: pointer; }}
            .btn-maps {{ text-decoration: none; background: white; border: 1.5px solid #1a73e8; color: #1a73e8; padding: 8px 12px; border-radius: 8px; font-size: 16px; }}
            
            /* Mode FAIT */
            .done {{ opacity: 0.5; background: #e5e7eb !important; border-left-color: #9ca3af !important; transform: scale(0.98); }}
            .done .btn-valider {{ background: #22c55e !important; color: white !important; border: none !important; }}
            
            /* MODE COMPACT */
            .compact-mode .card {{ padding: 6px 12px; }}
            .compact-mode .client-nom {{ font-size: 13px; }}
            .compact-mode .client-adr {{ font-size: 11px; }}
            .compact-mode .btn-valider {{ padding: 6px 10px; font-size: 10px; }}
            
            .controls {{ display: flex; gap: 8px; }}
            .btn-top {{ border: none; padding: 8px 12px; border-radius: 8px; font-size: 11px; font-weight: bold; cursor: pointer; color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2 style="margin:0; color:#1a73e8; font-size:18px;">🗞️ MA TOURNÉE</h2>
            <div class="controls">
                <button onclick="toggleCompact()" class="btn-top" style="background:#4b5563;">🔍 VUE</button>
                <button onclick="resetAll()" class="btn-top" style="background:#ef4444;">🔄 RESET</button>
            </div>
        </div>
        
        <div id="main-list">{cards_html}</div>

        <script>
            function markDone(id) {{
                const card = document.getElementById('card' + id);
                const btn = document.getElementById('btn' + id);
                card.classList.toggle('done');
                btn.innerHTML = card.classList.contains('done') ? '✅ FAIT' : 'VALIDER';
            }}
            
            function toggleCompact() {{
                document.getElementById('main-list').classList.toggle('compact-mode');
            }}

            function resetAll() {{
                if(confirm('Réinitialiser toute la liste ?')) {{
                    const cards = document.querySelectorAll('.card');
                    cards.forEach(c => {{
                        c.classList.remove('done');
                        const btn = c.querySelector('.btn-valider');
                        btn.innerHTML = 'VALIDER';
                    }});
                }}
            }}
        </script>
    </body>
    </html>
    """

st.title("🗞️ Ma Tournée RL - Config")

st.info("Colle ta liste PDF ici. Format : NOM ; ADRESSE ; OPTION")
data_input = st.text_area("Liste des clients :", height=300)

if st.button("🚀 GÉNÉRER L'APPLI FINALE"):
    if data_input:
        html_code = generate_final_html(data_input.split("\n"))
        st.success("Application complète générée !")
        st.download_button("📥 TÉLÉCHARGER LE FICHIER", html_code, "MaTournee_RL.html", "text/html")