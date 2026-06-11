import sys
with open(r'C:\Users\Alber\Music\VIGILANCIA\calendario.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the selectbox and text_area to add keys
old_selectbox = 'nuevo_est = st.selectbox("Actualizar Estado:", opciones_est, index=idx_est)'
new_selectbox = 'nuevo_est = st.selectbox("Actualizar Estado:", opciones_est, index=idx_est, key=f"sel_est_{idx}")'

old_textarea = 'nuevo_res = st.text_area("Resultados de la Investigación de Campo:", value=res_previo if res_previo != "nan" else "")'
new_textarea = 'nuevo_res = st.text_area("Resultados de la Investigación de Campo:", value=res_previo if res_previo != "nan" else "", key=f"txt_res_{idx}")'

old_button = 'if st.form_submit_button("💾 Guardar Investigación"):'
new_button = 'if st.form_submit_button("💾 Guardar Investigación", key=f"btn_vbc_{idx}"):'

content = content.replace(old_selectbox, new_selectbox)
content = content.replace(old_textarea, new_textarea)
content = content.replace(old_button, new_button)

with open(r'C:\Users\Alber\Music\VIGILANCIA\calendario.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Keys added successfully')
