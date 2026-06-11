import sys
import pandas as pd
from datetime import datetime
sys.path.append(r'C:\Users\Alber\Music\VIGILANCIA')
import calendario

try:
    df_vbc = calendario.cargar_datos('VBC_Rumores')
    idx = 0 # sincelejo
    row = df_vbc.iloc[idx]
    estado_actual = str(row.get('Estado_Verificacion', '🔴 Pendiente de Verificación'))
    nuevo_est = "🟢 Confirmado - Brote Activo"
    nuevo_res = "Probando script."

    # Lógica de Escalamiento a ERI
    if "Brote Activo" in nuevo_est and "Brote Activo" not in estado_actual:
        df_brotes = calendario.cargar_datos('Brotes_ERI')
        nuevo_brote = pd.DataFrame([{
            "Fecha_Alerta": datetime.today().strftime("%Y-%m-%d"), 
            "Municipio": str(row.get("Municipio", "N/A")),
            "Patologia": str(row.get("Tipo_Sindrome", "N/A")) + " (Desde VBC)", 
            "Fuente": "Alerta Comunitaria: " + str(row.get("Fuente_Reporte", "N/A")), 
            "Descripcion": str(row.get("Descripcion_Evento", "")) + "\n[Inv. Campo]: " + str(nuevo_res),
            "Equipo_Asignado": "Pendiente", 
            "Estado": "🔴 ACTIVO", 
            "Ruta_ERI": ""
        }])
        
        # Test concat
        final_df = pd.concat([df_brotes, nuevo_brote], ignore_index=True)
        calendario.guardar_datos(final_df, 'Brotes_ERI')
        print("Success Escalation!")
    else:
        print("Not escalated")
except Exception as e:
    import traceback
    traceback.print_exc()
