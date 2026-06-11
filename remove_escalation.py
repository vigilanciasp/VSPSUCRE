import re
import sys

with open(r'C:\Users\Alber\Music\VIGILANCIA\calendario.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = 'st.session_state["mensaje_exito_temp"] = "✅ Investigación guardada correctamente."\n                                st.rerun()'
content = re.sub(r'# L.gica de Escalamiento a ERI[\s\S]*?st\.rerun\(\)', replacement, content)

with open(r'C:\Users\Alber\Music\VIGILANCIA\calendario.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Escalation removed using regex')
