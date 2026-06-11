import sys
with open(r'C:\Users\Alber\Music\VIGILANCIA\calendario.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = '''                                if "Brote Activo" in nuevo_est and "Brote Activo" not in estado_actual:
                                    df_brotes = cargar_datos('Brotes_ERI')
                                    nuevo_brote = pd.DataFrame([{
                                        "Fecha_Alerta": datetime.today().strftime("%Y-%m-%d"), "Municipio": row.get('Municipio', 'N/A'),
                                        "Patologia": f"Alerta Comunitaria: {row.get('Tipo_Sindrome', 'N/A')}", "Fuente": "VBC", "Descripcion": row.get('Descripcion_Evento', ''),
                                        "Equipo_Asignado": row.get('Responsable_Verificacion', 'Pendiente'), "Estado": "🟢 ACTIVO", "Ruta_ERI": ""
                                    }])
                                    guardar_datos(pd.concat([df_brotes, nuevo_brote], ignore_index=True), 'Brotes_ERI')
                                    registrar_log("Alerta VBC escalada automáticamente a Brotes ERI", "Vigilancia Comunitaria")
                                    st.session_state["mensaje_exito_temp"] = "✅ Rumor verificado y ESCALADO automáticamente al equipo de Brotes ERI."
                                else:
                                    st.session_state["mensaje_exito_temp"] = "✅ Investigación guardada correctamente."
                                st.rerun()'''

new_code = '''                                if "Brote Activo" in nuevo_est and "Brote Activo" not in estado_actual:
                                    df_brotes = cargar_datos('Brotes_ERI')
                                    nuevo_brote = pd.DataFrame([{
                                        "Fecha_Alerta": datetime.today().strftime("%Y-%m-%d"), "Municipio": row.get('Municipio', 'N/A'),
                                        "Patologia": f"Alerta Comunitaria: {row.get('Tipo_Sindrome', 'N/A')}", "Fuente": "VBC", "Descripcion": row.get('Descripcion_Evento', ''),
                                        "Equipo_Asignado": row.get('Responsable_Verificacion', 'Pendiente'), "Estado": "🟢 ACTIVO", "Ruta_ERI": ""
                                    }])
                                    guardar_datos(pd.concat([df_brotes, nuevo_brote], ignore_index=True), 'Brotes_ERI')
                                    registrar_log("Alerta VBC escalada automáticamente a Brotes ERI", "Vigilancia Comunitaria")
                                    st.session_state["mensaje_exito_temp"] = "✅ Rumor verificado y ESCALADO automáticamente al equipo de Brotes ERI."
                                else:
                                    st.session_state["mensaje_exito_temp"] = "✅ Investigación guardada correctamente."
                                st.balloons()
                                st.rerun()'''

content = content.replace(old_code, new_code)
with open(r'C:\Users\Alber\Music\VIGILANCIA\calendario.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Added balloons successfully')
