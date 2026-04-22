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
        badge = f'<div class="badge-stop">⚠️ PAS DE JOURNAL LE LUNDI</div>' if is_stop else ""
        border_color = "#ef4444" if is_stop else "#1a73e8"
        
        clean_adr = adr.replace(" ", "+")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={clean_adr}"
        
        cards_html += f"""
        <div class="card" id="card{i}" style="border-left: 6px solid {border_color};">
            <div class="card-content">
                <div class="client-nom">{nom}</div>
                <div class="client-adr">{adr}</div>
                {badge}
            </div>
            <div class="card-btns">
                <button onclick="markDone({i})" id="btn{i}" class="btn-valider">VALIDER</button>
                <a href="{maps_url}" target="_blank" class="btn-maps">📍</a>
            </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #f0f2f5; padding: 10px; margin: 0; }}
            
            /* Header Fixe */
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; position: sticky; top: 0; background: #f0f2f5; padding: 10px 5px; z-index: 1000; border-bottom: 2px solid #ddd; }}
            .controls {{ display: flex; gap: 10px; }}
            .btn-top {{ border: none; padding: 10px 15px; border-radius: 8px; font-size: 12px; font-weight: bold; cursor: pointer; color: white; }}

            /* Style des Cartes */
            .card {{ background: white; margin-bottom: 10px; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
            .card-content {{ flex: 1; }}
            .client-nom {{ font-size: 15px; font-weight: 800; color: #1a73e8; }}
            .client-adr {{ font-size: 12px; color: #4b5563; font-weight: 600; }}
            .badge-stop {{ color: #ef4444; font-weight: bold; font-size: 11px; margin-top: 4px; }}
            
            /* Boutons Actions */
            .card-btns {{ display: flex; align-items: center; gap: 10px; margin-left: 10px; }}
            .btn-valider {{ background: #f3f4f6; border: 1px solid #d1d5db; padding: 12px 10px; border-radius: 8px; font-size: 11px; font-weight: bold; cursor: pointer; min-width: 85px; }}
            .btn-maps {{ text-decoration: none; border: 2px solid #1a73e8; color: #1a73e8; padding: 8px 12px; border-radius: 8px; font-size: 18px; line-height: 1; }}
            
            /* États Spéciaux */
            .done {{ opacity: 0.5; background: #d1fae5 !important; border-left-color: #9ca3af !important; }}
            .done .btn-valider {{ background: #22c55e !important; color: white; border: none; }}
            
            .compact-mode .card {{ padding: 8px 15px; margin-bottom: 5px; }}
            .compact-mode .client-nom {{ font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <span style="font-weight:bold; color:#1a73e8;">🗞️ MA TOURNÉE</span>
            <div class="controls">
                <button onclick="toggleCompact()" class="btn-top" style="background:#4b5563;">🔍 VUE</button>
                <button onclick="resetAll()" class="btn-top" style="background:#ef4444;">🔄 RESET</button>
            </div>
        </div>
        
        <div id="liste-container">{cards_html}</div>

        <script>
            function markDone(id) {{
                var card = document.getElementById('card' + id);
                var btn = document.getElementById('btn' + id);
                if (card.classList.contains('done')) {{
                    card.classList.remove('done');
                    btn.innerHTML = 'VALIDER';
                }} else {{
                    card.classList.add('done');
                    btn.innerHTML = '✅ FAIT';
                }}
            }}
            
            function toggleCompact() {{
                document.getElementById('liste-container').classList.toggle('compact-mode');
            }}

            function resetAll() {{
                if(confirm('Tout recommencer ?')) {{
                    var cards = document.getElementsByClassName('card');
                    for(var i=0; i<cards.length; i++) {{
                        cards[i].classList.remove('done');
                        var btns = cards[i].getElementsByTagName('button');
                        if(btns.length > 0) btns[0].innerHTML = 'VALIDER';
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    """

st.title("🗞️ Configurateur Tournée")
data_input = st.text_area("Colle ta liste ici (NOM ; ADRESSE ; OPTION) :", height=300)

if st.button("🚀 GÉNÉRER L'APPLI"):
    if data_input:
        html_code = generate_final_html(data_input.split("\n"))
        st.download_button("📥 TÉLÉCHARGER", html_code, "MaTournee.html", "text/html")