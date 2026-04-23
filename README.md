if st.button("📱 GÉNÉRER LE FICHIER MOBILE", use_container_width=True):
        if data_input and data_input != default_text:
            final_html = generate_html_ritter(data_input, compact)
            st.download_button("📥 TÉLÉCHARGER LE FICHIER", final_html, "Tournee.html", "text/html")
        else:
            st.warning("Veuillez entrer des données valides.")