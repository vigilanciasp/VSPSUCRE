import sys
import re

path = r'C:\Users\Alber\Music\VIGILANCIA\calendario.py'
try:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    encoding = 'utf-8'
except UnicodeDecodeError:
    with open(path, 'r', encoding='latin-1') as f:
        c = f.read()
    encoding = 'latin-1'

# We replace the line
c = re.sub(
    r'secciones_6\s*=\s*\[[^\]]+\]',
    'secciones_6 = ["🦠 Brotes y ERI", "🛑 Tablero de Problemas", "🤖 Asistente Redactor VSP", "🪦 Sala de Mortalidades"]',
    c
)

with open(path, 'w', encoding=encoding) as f:
    f.write(c)
print("Regex replaced successfully")
