import sys
import re

path = r'C:\Users\Alber\Music\VIGILANCIA\calendario.py'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    c = f.read()

# Buscamos el mapeo_vistas = { ... } al final del archivo
if '"📝 Registrar Actividad": vista_registrar_actividad,' in c or '"📅 Registrar Actividad": vista_registrar_actividad,' in c or 'vista_registrar_actividad' in c:
    # Agregamos la entrada justo después de Asistente Redactor VSP
    c = re.sub(
        r'("\S+\s+Asistente Redactor VSP": vista_asistente_ia,)',
        r'\1\n    "🪦 Sala de Mortalidades": vista_sala_mortalidades,',
        c
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("Mapeo actualizado")
else:
    print("No se encontró mapeo")
