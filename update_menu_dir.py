import re

with open(r'C:\Users\Alber\Music\VIGILANCIA\calendario.py', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Quitar el boton de Brotes y ERI
c = c.replace('"🌋 Brotes y ERI", ', '')
c = c.replace(', "🌋 Brotes y ERI"', '')
c = c.replace('"🌋 Brotes y ERI"', '')
c = c.replace('    "🌋 Brotes y ERI": vista_brotes_eri,\n', '')

# 2. Modificar vista_directorio
old_dir_code = """    with t_lista:
        st.markdown("#### 🔗 Directorio Central en la Nube")
        st.link_button("🌐 Abrir Directorio Maestro Completo (Google Sheets)", URL_DIRECTORIO_ENTIDADES, use_container_width=True, type="primary")
        st.caption("Usa este botón para editar el directorio principal hospedado en línea.")
        st.markdown("---")
        
        st.markdown("#### 📋 Base de Datos Auxiliar de Contactos (Local)")
        if not df_dir.empty:"""

new_dir_code = """    with t_lista:
        st.markdown("#### 🔗 Directorio Central en la Nube")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.link_button("🌐 Abrir Directorio Maestro para Editar", URL_DIRECTORIO_ENTIDADES, use_container_width=True, type="primary")
        with col_btn2:
            if st.button("🔄 Sincronizar Datos desde la Nube", use_container_width=True):
                st.session_state.pop('df_directorio_nube', None)
        
        st.markdown("---")
        
        st.markdown("#### 📋 Base de Datos de Contactos (Sincronizada)")
        
        # Cargar desde Google Sheets dinámicamente
        if 'df_directorio_nube' not in st.session_state:
            url_csv = "https://docs.google.com/spreadsheets/d/12OoDlbA8L3uaAv0ZZqzSU08nLx0lzUf_/export?format=csv&gid=1427970023"
            try:
                df_nube = pd.read_csv(url_csv, skiprows=1)
                # Limpiar las columnas (el archivo real tiene MUNICIPIO, NOMBRE Y APELLIDOS, TELÉFONO, CORREO ELECTRONICO)
                df_nube = df_nube.rename(columns={
                    "NOMBRE Y APELLIDOS": "Nombre",
                    "TELÉFONO": "Telefono",
                    "CORREO ELECTRONICO": "Correo",
                    "MUNICIPIO": "Municipio"
                })
                df_nube = df_nube.dropna(subset=["Municipio", "Nombre"], how="all")
                df_nube["Entidad"] = "Institucional" # Valor por defecto si no existe en el sheet
                st.session_state['df_directorio_nube'] = df_nube
            except Exception as e:
                st.error(f"No se pudo cargar el directorio desde la nube. Mostrando datos locales. Detalle: {e}")
                st.session_state['df_directorio_nube'] = df_dir
                
        df_act = st.session_state['df_directorio_nube']
        
        if not df_act.empty:"""

# Ensure df_dir -> df_act in the rest of the dataframe viewing logic
c = c.replace(old_dir_code, new_dir_code)
# Reemplazar df_dir["Municipio"] por df_act["Municipio"]
c = c.replace('sorted(df_dir["Municipio"].dropna().unique().tolist())', 'sorted(df_act["Municipio"].astype(str).dropna().unique().tolist())')
c = c.replace('sorted(df_dir["Entidad"].dropna().unique().tolist())', 'sorted(df_act.get("Entidad", pd.Series(["Institucional"])).dropna().unique().tolist())')
c = c.replace('df_mostrar = df_dir.copy()', 'df_mostrar = df_act.copy()')

with open(r'C:\Users\Alber\Music\VIGILANCIA\calendario.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated menu and directory')
