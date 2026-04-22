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
        <div class="card" id="card{i}" style="border-left: 8px solid {border_color};">
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
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ font-family: sans-serif; background: #f0f2f5; padding: 10px; margin: 0; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; position: sticky; top: 0; background: #f0f2f5; padding: 10px 0; z-index: 100; }}
            .btn-top {{ border: none; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: bold; cursor: pointer; color: white; }}
            
            .card {{ background: white; margin-bottom: 10px; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }}
            .client-nom {{ font-size: 16px; font-weight: 800; color: #1a73e8; }}
            .client-adr {{ font-size: 13px; color: #4b5563; }}
            .badge-stop {{ color: #ef4444; font-weight: bold; font-size: 12px; }}
            
            .btn-valider {{ background: #eee; border: 1px solid #ccc; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; }}
            .btn-maps {{ text-decoration: none; border: 2px solid #1a73e8; padding: 8px; border-radius: 8px; font-size: 20px; }}
            
            /* État Validé */
            .done {{ background: #d1fae5 !important; opacity: 0.6; }}
            .done .btn-valider {{ background: #22c55e !important; color: white; border: none; }}
            
            /* Mode Compact */
            .compact-mode .card {{ padding: 5px 15px; margin-bottom: 5px; }}
            .compact-mode .client-nom {{ font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <strong style="color:#1a73e8;">🗞️ MA TOURNÉE</strong>
            <div>
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
                    btn.innerText = 'VALIDER';
                }} else {{
                    card.classList.add('done');
                    btn.innerText = '✅ FAIT';
                }}
            }}
            
            function toggleCompact() {{
                document.getElementById('liste-container').classList.toggle('compact-mode');
            }}

            function resetAll() {{
                if(confirm('Réinitialiser ?')) {{
                    var cards = document.getElementsByClassName('card');
                    for(var i=0; i<cards.length; i++) {{
                        cards[i].classList.remove('done');
                        var btn = cards[i].getElementsByTagName('button')[0];
                        btn.innerText = 'VALIDER';
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    """

st.title("🗞️ Configurateur Final")
data_input = st.text_area("Colle ta liste ici :", height=300)

if st.button("🚀 GÉNÉRER"):
    if data_input:
        html = generate_final_html(data_input.split("\n"))
        st.download_button("📥 TÉLÉCHARGER", html, "Tournee.html", "text/html")