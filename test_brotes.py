import sys
import pandas as pd
sys.path.append(r'C:\Users\Alber\Music\VIGILANCIA')
import calendario

df_brotes = calendario.cargar_datos('Brotes_ERI')
print('Dataframe loaded. Empty?', df_brotes.empty)
print(df_brotes.columns)
print(df_brotes)

if not df_brotes.empty:
    opciones_b = [f"{idx} - {row['Patologia']} en {row['Municipio']} ({row['Estado']})" for idx, row in df_brotes.iterrows()]
    print('Opciones:', opciones_b)
    
    idx_b = int(opciones_b[0].split(' - ')[0])
    fila_b = df_brotes.iloc[idx_b]
    print('Fila B:', fila_b)
    
    print('Eq asig:', fila_b['Equipo_Asignado'], type(fila_b['Equipo_Asignado']))
    print('Estado:', fila_b['Estado'], type(fila_b['Estado']))
