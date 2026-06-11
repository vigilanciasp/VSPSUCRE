import sys
import pandas as pd
sys.path.append(r'C:\Users\Alber\Music\VIGILANCIA')
import calendario

df_brotes = calendario.cargar_datos('Brotes_ERI')

try:
    if not df_brotes.empty:
        opciones_b = [f"{idx} - {str(row.get('Patologia', ''))} en {str(row.get('Municipio', ''))} ({str(row.get('Estado', ''))})" for idx, row in df_brotes.iterrows()]
        
        idx_b = int(opciones_b[len(opciones_b)-1].split(' - ')[0])
        fila_b = df_brotes.iloc[idx_b]
        
        eq_asig = fila_b.get("Equipo_Asignado", "")
        # En Streamlit st.text_area(value=...) si value es float('nan') crashea.
        if pd.isna(eq_asig):
            raise ValueError("Equipo_Asignado es NaN, esto crashea Streamlit st.text_area")
            
        estado = fila_b.get("Estado", "")
        if pd.isna(estado):
            raise ValueError("Estado es NaN")
            
        print("Success, no exceptions raised.")
except Exception as e:
    import traceback
    traceback.print_exc()
