import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import io
import os
import urllib.parse
import plotly.express as px
from fpdf import FPDF
# ==========================================
# 1. CONFIGURACIÓN E INYECCIÓN DE ESTILOS CSS
# ==========================================
st.set_page_config(layout="wide", page_title="Planificación VSP Sucre", page_icon="📅")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Ocultar elementos nativos de Streamlit para un look app */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container { 
        padding-top: 1rem; 
        max-width: 95%;
    }
    
    h1, h2, h3, h4, h5 {
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Botones Globales Premium */
    .stButton>button {
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
        filter: brightness(1.1);
    }
    
    /* Tarjetas de Métricas KPI */
    .metric-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-align: center;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.7);
        border: 1px solid rgba(14, 165, 233, 0.3);
    }
    .metric-card h3 {
        font-size: 2.5rem;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
        font-weight: 800 !important;
    }
    
    /* Contenedores Genéricos (Herramientas / Accesos) */
    .tool-container {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px;
        box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
    }
    
    .custom-card {
        padding: 20px; 
        border-radius: 16px; 
        background: rgba(30, 41, 59, 0.5); 
        backdrop-filter: blur(12px);
        margin-bottom: 15px; 
        border-left: 5px solid #0ea5e9;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        border-top: 1px solid rgba(255,255,255,0.05);
        border-right: 1px solid rgba(255,255,255,0.05);
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .custom-card:hover {
        background: rgba(30, 41, 59, 0.8); 
        transform: scale(1.02);
    }
    
    /* Pestañas (Tabs) Estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding: 10px 0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255,255,255,0.03);
        border-radius: 10px 10px 0 0;
        padding: 10px 24px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255,255,255,0.08);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(0deg, rgba(14, 165, 233, 0.15) 0%, transparent 100%);
        border-bottom: 3px solid #0ea5e9 !important;
        color: #38bdf8 !important;
    }
    
    /* Títulos Principales */
    .main-title {
        background: -webkit-linear-gradient(45deg, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0px;
        line-height: 1.1;
    }
    .sub-title {
        color: #0ea5e9;
        font-weight: 600;
        letter-spacing: 1px;
        font-size: 0.95rem;
        text-transform: uppercase;
        margin-top: 8px;
    }
    
    /* Calendario */
    .fc-day-sat, .fc-day-sun {
        background-color: rgba(239, 68, 68, 0.05) !important;
    }
    .fc-event {
        white-space: normal !important;
        overflow: visible !important;

        font-size: 0.85rem !important;
        line-height: 1.3 !important;
        padding: 6px 10px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .fc-event-title { font-weight: 600 !important; }
    .fc-daygrid-event { margin-top: 5px !important; margin-bottom: 5px !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONSTANTES Y CONFIGURACIONES GLOBALES
# ==========================================
# Si estamos en Railway/Docker, usamos una subcarpeta para el volumen persistente
DATA_DIR = "data/" if os.environ.get("RAILWAY_ENVIRONMENT") or os.path.exists("/app") else ""
if DATA_DIR and not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

ARCHIVO_DB = os.path.join(DATA_DIR, "base_datos_vsp_sucre.xlsx")
CARPETA_SOPORTES = os.path.join(DATA_DIR, "soportes_compromisos")
ENLACE_PORTAL_WEB = "https://sivigilaweb.ins.gov.co/Sivigila/"  
CORREO_DESTINO_HC = "vsp.historiasclinicas@sucre.gov.co"  

# --- CONFIGURACIÓN DE FORMULARIOS GOOGLE FORMS ---
BASE_GOOGLE_FORMS = "https://docs.google.com/forms/d/e/1FAIpQLSc1o7tjgmWqKhdTV1HuYTqJkSa3KPHI2BWQNrJ3zT9zndvX6A/viewform" 
ID_TEMA_FORM = "entry.67209856"
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/162S8gANBLi-d3oKJZKieFl0ff46flPYwE8U5zoE7XUI/edit?resourcekey=&gid=621967594#gid=621967594" 
URL_DIRECTORIO_ENTIDADES = "https://docs.google.com/spreadsheets/d/12OoDlbA8L3uaAv0ZZqzSU08nLx0lzUf_/edit?rtpof=true&sd=true&gid=1427970023#gid=1427970023"
URL_CONSECUTIVOS = "https://docs.google.com/spreadsheets/d/16jQlyAyO514qPppE6Tu6ThhWxqW1CHB0wLWE1FeYhKY/edit?usp=drivesdk"

if not os.path.exists(CARPETA_SOPORTES):
    os.makedirs(CARPETA_SOPORTES)

# --- LISTAS DE DATOS MAESTROS ---
import json
import os

ARCHIVO_LISTAS = "listas_maestras.json"
DEFAULT_LISTAS = {
    "LISTA_RESPONSABLES": [
        "Seleccione...", "ADALGISA PATRON CONDE", "ANA GABRIELA DIAZ ANAYA", "ANA LUCIA MENDOZA TAMARA", 
        "BALDIR PABA OSORIO", "LILIBETH DAZA CAMELO", "EDER JESUS PATERNINA RODRIGUEZ", "ELIANA CECILIA MORALES MELENDEZ", 
        "ENITT DEL ROSARIO HERNANDEZ DORIAS", "ESPERANZA DEL PILAR VARGAS VARGAS", "HECTOR FABIO RENTERIA", 
        "ISAAC JACOB VELASQUEZ DOMINGUEZ", "JAVIER MAURICIO CORREA PATERNOSTRO", "KAREN MARGARITA ALDANA ARRIETA", 
        "KEVIN ALBERTO BARBARAN ALVAREZ", "LEVY SUNILDA CAMPO LASSO", "LOLI LUZ SIERRA DIAZ", "LORENA PORTILLO CUENTAS", 
        "LUCIA CLARETH HERNANDEZ PEREZ", "LUISA FERNANDA REYES DÍAZ", "LUZMILA VILLAMIZAR MOLINA", 
        "MARIA CANDELARIA MEJIA LOPEZ", "MARIA JOSE CANTILLO ROYERO", "MARLON ESPITIA CERPA", 
        "MARTHA CECILIA MELENDEZ MARTINEZ", "MERY DE JESUS NARVAEZ ASSIA", "NICOLASA MARGARITA ARRIETA SERPA", 
        "NURYS CONCEPCIÓN HERRERA GUTIÉRREZ", "VIRGINIA OLIVERO GARCIA", "YARLENY ESTHER BERRIO ACOSTA", 
        "MARIA JOSE PEÑARANDA", "BRENDER BARRIOS", "ANA KARINA PEÑATES DE ARCE", "DINO VERGARA PEREZ", 
        "JUAN CARLOS GARCIA VIVERO", "MANUEL ORTEGA HERNANDEZ", "MARIA CAMPO", "VILMA MERCADO CUMPLIDO"
    ],
    "LISTA_MUNICIPIOS": [
        "Seleccione...", "Buenavista", "Caimito", "Chalán", "Colosó", "Corozal", "Coveñas", "El Roble", 
        "Galeras", "Guaranda", "La Unión", "Los Palmitos", "Majagual", "Morroa", "Ovejas", "Palmito", 
        "Sampués", "San Benito Abad", "San Juan de Betulia", "San Marcos", "San Onofre", "San Pedro", 
        "Sincé", "Sincelejo", "Sucre", "Tolú", "Toluviejo"
    ],
    "LISTA_LUGARES": ["Seleccione...", "Sala Situacional", "Auditorio Panzigua", "Otro"],
    "LISTA_TIPOS_EVENTO": [
        "ASISTENCIA TECNICA", "BAC", "BAI", "CAPACITACION", "COMITÉ ESTADISTICAS VITALES", 
        "COMITÉ SANIDAD PORTUARIA", "COVE", "IEC", "MESA DE TRABAJO", "MONITOREO", "REUNION", 
        "SAR", "SEGUIMIENTO", "UNIDAD DE ANALISIS", "OTRO"
    ],
    "LISTA_EISP": [
        "Gestión Institucional / Transversal", "Dengue (210)", "Malaria (465)", "Chagas (205)",
        "Mortalidad Materna (551)", "Mortalidad Perinatal (560)", "Infección Respiratoria Aguda - IRA (345)",
        "Vigilancia de Violencias de Género (875)", "Tuberculosis (810)", "VIF / Salud Mental (900)"
    ]
}

def cargar_listas():
    # Detectar entorno Railway o local
    ruta = "/app/data/listas_maestras.json" if os.path.exists("/app/data") else ARCHIVO_LISTAS
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_LISTAS, f, ensure_ascii=False, indent=4)
    return DEFAULT_LISTAS

def guardar_listas(datos):
    ruta = "/app/data/listas_maestras.json" if os.path.exists("/app/data") else ARCHIVO_LISTAS
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

listas_dinamicas = cargar_listas()
LISTA_RESPONSABLES = listas_dinamicas.get("LISTA_RESPONSABLES", DEFAULT_LISTAS["LISTA_RESPONSABLES"])
LISTA_MUNICIPIOS = listas_dinamicas.get("LISTA_MUNICIPIOS", DEFAULT_LISTAS["LISTA_MUNICIPIOS"])
LISTA_LUGARES = listas_dinamicas.get("LISTA_LUGARES", DEFAULT_LISTAS["LISTA_LUGARES"])
LISTA_TIPOS_EVENTO = listas_dinamicas.get("LISTA_TIPOS_EVENTO", DEFAULT_LISTAS["LISTA_TIPOS_EVENTO"])
LISTA_EISP = listas_dinamicas.get("LISTA_EISP", DEFAULT_LISTAS["LISTA_EISP"])

# ==========================================
# 3. CAPA DE CONTROL DE PERSISTENCIA (EXCEL)
# ==========================================
def inicializar_db():
    esquema = {
        'Eventos': ["Fecha", "Hora Inicio", "Hora Fin", "Responsable", "Tipo de Evento", "Municipio", "Lugar", "Vehículo", "Estado", "Observaciones"],
        'Disponibilidad': ["Semana_Inicio", "Integrantes", "Cargos", "Laboratorio_Responsable", "Laboratorio_Cargo"],
        'Compromisos': ["Fecha_Acuerdo", "Compromiso", "Responsable", "Plazo", "Estado", "Respuesta_Avance", "Ruta_Soporte"],
        'Actas': ["Fecha_Acta", "Tipo_Comite", "Responsable_Acta", "Asistentes", "Temas", "Conclusiones_Compromisos"],
        'Alertas_Inventario': ["Fecha_Registro", "Tipo_Item", "Titulo_Nombre", "Descripcion_Cantidad", "Clasificacion_Riesgo"],
        'Historial_Enlaces': ["Fecha_Registro", "Tipo_Evento", "Tema_Evento", "Responsable_Ponente", "Enlace_Formulario"],
        'Usuarios': ["Usuario", "Contrasena", "Nombre_Completo", "Rol"],
        'VBC_Rumores': ['Fecha_Reporte', 'Municipio', 'Comunidad_Vereda', 'Tipo_Sindrome', 'Fuente_Reporte', 'Descripcion_Evento', 'Estado_Verificacion', 'Responsable_Verificacion'],
        'Directorio_Contactos': ['Nombre', 'Entidad', 'Municipio', 'Correo', 'Telefono', 'Rol'],
        'Solicitudes_Externas': ['Fecha_Solicitud', 'Tipo_Solicitud', 'Paciente', 'Identificacion', 'EAPB', 'Municipio', 'Responsable_Solicitud', 'Estado', 'Ruta_Documento'],
        'Solicitudes_Teams': ['Fecha_Solicitud', 'Fecha_Evento', 'Tema', 'Responsable_Evento', 'Encargado_Links', 'Estado', 'Enlace_Teams'],
        'Brotes_ERI': ['Fecha_Alerta', 'Municipio', 'Patologia', 'Fuente', 'Descripcion', 'Equipo_Asignado', 'Estado', 'Ruta_ERI'],
        'Tablero_Problemas': ['Fecha_Reporte', 'Municipio', 'Categoria', 'Descripcion', 'Responsable', 'Estado', 'Respuesta'],
        'Auditoria_Logs': ['Fecha_Hora', 'Usuario', 'Accion', 'Modulo'],
        'Consecutivos_Actas': ['Fecha', 'Tipo_Documento', 'Consecutivo', 'Asunto', 'Responsable'],
        'Casos_Criticos': ['Fecha_Notificacion', 'Evento', 'Identificacion', 'Municipio', 'Fase', 'Dias_Mora'],
        'IPS_UPGD': ['Municipio', 'Nombre_IPS', 'Codigo_Sede', 'Reporto_Ultima_Semana', 'Fecha_Ultimo_Reporte'],
        'Boletines_Data': ['Semana', 'Municipio', 'Evento', 'Edad', 'Sexo', 'Casos'],
        'Muestras_Lab': ['Fecha_Envio', 'Paciente_Identificacion', 'Municipio', 'Tipo_Muestra', 'Evento_Sospechoso', 'Estado', 'Resultado', 'Dias_Espera'],
        'Riesgos_VSP': ['Fecha_Registro', 'Categoria', 'Descripcion', 'Municipio', 'Probabilidad', 'Impacto', 'Nivel_Riesgo', 'Responsable', 'Estado', 'Mitigacion'],
        'Cumpleanos': ['Funcionario', 'Fecha_Nacimiento']
    }
    
    if not os.path.exists(ARCHIVO_DB):
        with pd.ExcelWriter(ARCHIVO_DB, engine='openpyxl') as writer:
            for hoja, columnas in esquema.items():
                if hoja == 'Usuarios':
                    # Crear administrador maestro por defecto
                    df_admin_init = pd.DataFrame([{"Usuario": "admin", "Contrasena": "Vsp26", "Nombre_Completo": "ADMINISTRADOR PRINCIPAL", "Rol": "Administrador Total"}])
                    df_admin_init.to_excel(writer, sheet_name=hoja, index=False)
                else:
                    pd.DataFrame(columns=columnas).to_excel(writer, sheet_name=hoja, index=False)
    else:
        try:
            todas_las_hojas = pd.read_excel(ARCHIVO_DB, sheet_name=None)
            hojas_actuales = list(todas_las_hojas.keys())
            
            hojas_faltantes = [hoja for hoja in esquema.keys() if hoja not in hojas_actuales]
            
            if hojas_faltantes:
                for hoja in hojas_faltantes:
                    columnas = esquema[hoja]
                    if hoja == 'Usuarios':
                        todas_las_hojas[hoja] = pd.DataFrame([{"Usuario": "admin", "Contrasena": "Vsp26", "Nombre_Completo": "ADMINISTRADOR PRINCIPAL", "Rol": "Administrador Total"}])
                    else:
                        todas_las_hojas[hoja] = pd.DataFrame(columns=columnas)
                        
                with pd.ExcelWriter(ARCHIVO_DB, engine='openpyxl') as writer:
                    for n_hoja, d_hoja in todas_las_hojas.items():
                        d_hoja.to_excel(writer, sheet_name=n_hoja, index=False)
        except Exception as e:
            st.error(f"Error crítico en chequeo de base de datos: {e}")

@st.cache_data(show_spinner=False)
def cargar_datos(hoja):
    try:
        if not os.path.exists(ARCHIVO_DB):
            inicializar_db()
        df = pd.read_excel(ARCHIVO_DB, sheet_name=hoja)
        if hoja == 'Usuarios' and 'Permisos' not in df.columns:
            df['Permisos'] = "🏠 Inicio,📝 Registrar Actividad"
        return df.fillna("").astype(str) if hoja in ['Disponibilidad', 'Compromisos', 'Actas', 'Alertas_Inventario', 'Historial_Enlaces', 'Usuarios', 'VBC_Rumores', 'Directorio_Contactos', 'Solicitudes_Externas', 'Solicitudes_Teams', 'Brotes_ERI', 'Tablero_Problemas', 'Auditoria_Logs', 'Riesgos_VSP', 'Cumpleanos'] else df.fillna("")
    except Exception as e:
        st.error(f"Error al leer la pestaña {hoja}: {e}")
        return pd.DataFrame()

def guardar_datos(df, hoja):
    try:
        if os.path.exists(ARCHIVO_DB):
            todas_las_hojas = pd.read_excel(ARCHIVO_DB, sheet_name=None)
        else:
            todas_las_hojas = {}
        
        todas_las_hojas[hoja] = df
        
        with pd.ExcelWriter(ARCHIVO_DB, engine='openpyxl') as writer:
            for n_hoja, d_hoja in todas_las_hojas.items():
                d_hoja.to_excel(writer, sheet_name=n_hoja, index=False)
                
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error de escritura en disco: {e}")
        return False

# ==========================================
# 4. FUNCIONES AUXILIARES
# ==========================================
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def registrar_log(accion, modulo="General"):
    try:
        usuario = st.session_state.get("usuario_conectado", "Sistema")
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df_logs = cargar_datos('Auditoria_Logs')
        nuevo_log = pd.DataFrame([{"Fecha_Hora": fecha_hora, "Usuario": usuario, "Accion": accion, "Modulo": modulo}])
        guardar_datos(pd.concat([df_logs, nuevo_log], ignore_index=True), 'Auditoria_Logs')
    except Exception:
        pass

def generar_pdf_oficial(titulo, texto_cuerpo, autor):
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="GOBERNACION DE SUCRE", ln=True, align='C')
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="Secretaria de Salud Departamental - Vigilancia en Salud Publica", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt=titulo, ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", '', 12)
        texto_limpio = str(texto_cuerpo).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=texto_limpio)
        pdf.ln(20)
        
        pdf.set_font("Arial", 'I', 11)
        fecha_str = datetime.today().strftime('%d/%m/%Y %H:%M')
        pdf.cell(0, 10, txt=f"Documento generado automaticamente por Sistema VSP el {fecha_str}", ln=True)
        pdf.cell(0, 10, txt=f"Responsable / Funcionario: {autor}", ln=True)
        
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        import streamlit as st
        st.error(f"Error generando PDF: {e}")
        return None

def enviar_correo_outlook(destinatario, asunto, cuerpo, adjunto=None):
    try:
        from email.mime.application import MIMEApplication
        remitente = os.environ.get("EMAIL_SENDER") or (st.secrets["EMAIL_SENDER"] if "EMAIL_SENDER" in st.secrets else None)
        password = os.environ.get("EMAIL_PASSWORD") or (st.secrets["EMAIL_PASSWORD"] if "EMAIL_PASSWORD" in st.secrets else None)
        login_user = os.environ.get("EMAIL_LOGIN") or (st.secrets.get("EMAIL_LOGIN") if "EMAIL_LOGIN" in st.secrets else remitente)
        
        if not remitente or not password:
            return False, "Credenciales no configuradas. Agrega EMAIL_SENDER y EMAIL_PASSWORD en las variables de entorno de Railway."
        
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        if adjunto is not None:
            part = MIMEApplication(adjunto.getvalue(), Name=adjunto.name)
            part['Content-Disposition'] = f'attachment; filename="{adjunto.name}"'
            msg.attach(part)
        
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        # Iniciamos sesión con la cuenta principal real
        server.login(login_user, password)
        # Enviamos el mensaje indicando que proviene del alias
        server.send_message(msg)
        server.quit()
        return True, "Correo enviado correctamente."
    except Exception as e:
        return False, str(e)

def formatear_hora_12h(hora_str):
    try:
        return datetime.strptime(str(hora_str).strip(), "%H:%M").strftime("%I:%M %p").lower()
    except Exception:
        return str(hora_str)

def calcular_semaforo_compromiso(row):
    estado_act = str(row['Estado']).upper()
    if "CUMPLIDO" in estado_act or "FINALIZADO" in estado_act: 
        return "✅ FINALIZADO"
    try:
        plazo_dt = pd.to_datetime(row['Plazo']).date()
        hoy_dt = datetime.today().date()
        dias = (plazo_dt - hoy_dt).days
        if dias < 0: return "🔴 VENCIDO"
        elif dias <= 3: return f"🔴 CRÍTICO ({dias} d)"
        elif dias <= 7: return f"🟡 PRÓXIMO ({dias} d)"
        else: return f"🟢 EN TIEMPO ({dias} d)"
    except Exception:
        return str(row['Estado'])

def obtener_semana_epidemiologica(fecha): 
    return fecha.isocalendar()[1]

def generar_semanas_del_mes(anio, mes):
    semanas = []
    fecha_iter = datetime(anio, mes, 1)
    ultimo_dia = datetime(anio, 12, 31) if mes == 12 else datetime(anio, mes + 1, 1) - timedelta(days=1)
    lunes_inicial = fecha_iter - timedelta(days=fecha_iter.weekday())
    while lunes_inicial <= ultimo_dia:
        semanas.append((lunes_inicial, lunes_inicial + timedelta(days=6), obtener_semana_epidemiologica(lunes_inicial)))
        lunes_inicial += timedelta(days=7)
    return sorted(list(set(semanas)), key=lambda x: x[0])

inicializar_db()

# --- MANEJO ROBUSTO DE SESIÓN Y AUTENTICACIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_conectado" not in st.session_state:
    st.session_state["usuario_conectado"] = None
if "rol_conectado" not in st.session_state:
    st.session_state["rol_conectado"] = None
if "seccion_actual" not in st.session_state:
    st.session_state["seccion_actual"] = "🏠 Inicio"
if "fecha_seleccionada" not in st.session_state:
    st.session_state["fecha_seleccionada"] = datetime.today().strftime("%Y-%m-%d")
if "mensaje_exito_temp" not in st.session_state:
    st.session_state["mensaje_exito_temp"] = None
if "ultimo_link_virtual" not in st.session_state:
    st.session_state["ultimo_link_virtual"] = None
if "permisos_conectado" not in st.session_state:
    st.session_state["permisos_conectado"] = []

# ==========================================
# 5. CONTROL DE ACCESO (LOGIN) CENTRALIZADO
# ==========================================
if not st.session_state["autenticado"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        html_header = "<div class='metric-card' style='text-align: center; padding: 40px; border-top: 5px solid #2563eb; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 25px;'>"
        if os.path.exists("logo.png"):
            import base64
            with open("logo.png", "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            html_header += f"<img src='data:image/png;base64,{img_b64}' width='260' style='margin-bottom: 15px; border-radius: 8px; background-color: white; padding: 10px;'><br>"
        else:
            html_header += "<h1 style='font-size: 3rem; margin-bottom: 10px;'>🏢</h1>"
            
        html_header += "<h2 style='margin-bottom:5px; font-weight: 700; color: #f8fafc;'>Sistema Integral VSP</h2>"
        html_header += "<p style='color: #94a3b8; margin-bottom: 0px; font-size: 1.1rem;'>Plataforma Gerencial y Operativa</p>"
        html_header += "</div>"
        
        st.markdown(html_header, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            txt_user = st.text_input("👤 Usuario (Correo / ID):", key="login_user", autocomplete="username")
            txt_pass = st.text_input("🔑 Contraseña:", type="password", key="login_pass", autocomplete="current-password")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_login = st.form_submit_button("🔓 Ingresar al Sistema", use_container_width=True, type="primary")
        
        if btn_login:
            df_users_db = cargar_datos('Usuarios')
            validado = df_users_db[(df_users_db["Usuario"] == txt_user.strip()) & (df_users_db["Contrasena"] == txt_pass.strip())]
            
            if not validado.empty:
                st.session_state["autenticado"] = True
                st.session_state["mostrar_bienvenida"] = True
                st.session_state["usuario_conectado"] = validado.iloc[0]["Nombre_Completo"]
                st.session_state["rol_conectado"] = validado.iloc[0]["Rol"]
                
                # Cargar Permisos Dinámicos
                if "Permisos" in validado.columns and pd.notna(validado.iloc[0]["Permisos"]) and str(validado.iloc[0]["Permisos"]).strip() != "":
                    st.session_state["permisos_conectado"] = [p.strip() for p in str(validado.iloc[0]["Permisos"]).split(",") if p.strip()]
                else:
                    st.session_state["permisos_conectado"] = ["🏠 Inicio", "📝 Registrar Actividad"]
                
                registrar_log("Inicio de sesión exitoso", "Autenticación")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() # Bloquea el resto de la app hasta loguearse

if st.session_state.get("mostrar_bienvenida"):
    st.toast(f"👋 ¡Bienvenido(a) al sistema, {st.session_state['usuario_conectado']}!", icon="✅")
    st.session_state["mostrar_bienvenida"] = False

# ==========================================
# 6. ENCABEZADO Y SISTEMA DE NAVEGACIÓN POR ROLES
# ==========================================
col_logo, col_titulos, col_portal = st.columns([1, 4.5, 1])
with col_logo:
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo.png"): st.image("logo.png", width=120)
    else: st.markdown("### 🛡️ VSP")
with col_titulos:
    st.markdown("<h1 class='main-title'>Sistema de Planificación VSP</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Gobernación de Sucre • Dirección de Salud Pública</p>", unsafe_allow_html=True)
with col_portal:
    st.markdown("<div style='text-align: right; margin-top: 10px;'>", unsafe_allow_html=True)
    st.markdown(f"👤 <b style='color:#0ea5e9;'>{st.session_state.get('usuario_conectado', 'Invitado')}</b><br><small>{st.session_state.get('rol_conectado', '')}</small>", unsafe_allow_html=True)
    if st.button("🔒 Cerrar Sesión"):
        registrar_log("Cierre de sesión manual", "Autenticación")
        st.session_state["autenticado"] = False
        st.session_state["usuario_conectado"] = None
        st.session_state["rol_conectado"] = None
        st.session_state["permisos_conectado"] = []
        st.session_state["seccion_actual"] = "🏠 Inicio"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Grid de Navegación Dinámico según el Rol del Usuario conectado
nav_cols_1 = st.columns(4)
secciones_1 = ["🏠 Inicio", "📝 Registrar Actividad", "🛡️ Disponibilidad Semanal", "📋 Compromisos Técnicos"]
for idx, sec in enumerate(secciones_1):
    with nav_cols_1[idx]:
        if sec not in st.session_state.get("permisos_conectado", []) and st.session_state.get("rol_conectado") != "Administrador Total":
            st.button(sec, use_container_width=True, disabled=True)
        else:
            if st.button(sec, use_container_width=True, type="primary" if st.session_state["seccion_actual"] == sec else "secondary"):
                st.session_state["seccion_actual"] = sec; st.rerun()

# Segunda fila de botones que incluye el nuevo módulo exclusivo de gestión de usuarios
secciones_2 = ["🛠️ Enlaces y Solicitudes HC", "📄 Actas e Informes", "🚨 Alertas e Inventario", "🔍 Filtros y Dashboard"]
nav_cols_2 = st.columns(len(secciones_2))
for idx, sec in enumerate(secciones_2):
    with nav_cols_2[idx]:
        if sec not in st.session_state.get("permisos_conectado", []) and st.session_state.get("rol_conectado") != "Administrador Total":
            st.button(sec, use_container_width=True, disabled=True)
        else:
            if st.button(sec, use_container_width=True, type="primary" if st.session_state["seccion_actual"] == sec else "secondary"):
                st.session_state["seccion_actual"] = sec; st.rerun()

# Tercera fila para los módulos epidemiológicos y laboratorio
secciones_3 = ["🏘️ Vigilancia Comunitaria (VBC)", "📈 Tableros SIVIGILA", "🛡️ Calidad del Dato", "📞 Directorio de Red", "🧪 Muestras de Laboratorio"]
nav_cols_3 = st.columns(len(secciones_3))
for idx, sec in enumerate(secciones_3):
    with nav_cols_3[idx]:
        if sec not in st.session_state.get("permisos_conectado", []) and st.session_state.get("rol_conectado") != "Administrador Total":
            st.button(sec, use_container_width=True, disabled=True)
        else:
            if st.button(sec, use_container_width=True, type="primary" if st.session_state["seccion_actual"] == sec else "secondary"):
                st.session_state["seccion_actual"] = sec; st.rerun()

# Cuarta fila para módulos avanzados VSP
secciones_4 = ["🗺️ Georreferenciación", "📌 Kanban Críticos", "🏥 Silencio Epi", "🤖 Asistente Protocolos", "📊 Tablero Avanzado"]
nav_cols_4 = st.columns(len(secciones_4))
for idx, sec in enumerate(secciones_4):
    with nav_cols_4[idx]:
        if sec not in st.session_state.get("permisos_conectado", []) and st.session_state.get("rol_conectado") != "Administrador Total":
            st.button(sec, use_container_width=True, disabled=True)
        else:
            if st.button(sec, use_container_width=True, type="primary" if st.session_state["seccion_actual"] == sec else "secondary"):
                st.session_state["seccion_actual"] = sec; st.rerun()

# Quinta fila para panel de control y seguridad
secciones_5 = ["⚠️ Gestión del Riesgo", "⚙️ Panel Maestro y Roles", "🕵️ Auditoría y Logs"]
nav_cols_5 = st.columns(len(secciones_5))
for idx, sec in enumerate(secciones_5):
    with nav_cols_5[idx]:
        if sec not in st.session_state.get("permisos_conectado", []) and st.session_state.get("rol_conectado") != "Administrador Total":
            st.button(sec, use_container_width=True, disabled=True)
        else:
            if st.button(sec, use_container_width=True, type="primary" if st.session_state["seccion_actual"] == sec else "secondary"):
                st.session_state["seccion_actual"] = sec; st.rerun()

# Sexta fila para módulos misceláneos
secciones_6 = ["🦠 Brotes y ERI", "🛑 Tablero de Problemas", "🤖 Asistente Redactor VSP", "🪦 Sala de Mortalidades"]
if st.session_state.get("rol_conectado") == "Administrador Total":
    secciones_6.append("🎂 Gestionar Cumpleaños")
nav_cols_6 = st.columns(len(secciones_6))
for idx, sec in enumerate(secciones_6):
    with nav_cols_6[idx]:
        if sec not in st.session_state.get("permisos_conectado", []) and st.session_state.get("rol_conectado") != "Administrador Total":
            st.button(sec, use_container_width=True, disabled=True)
        else:
            if st.button(sec, use_container_width=True, type="primary" if st.session_state["seccion_actual"] == sec else "secondary"):
                st.session_state["seccion_actual"] = sec; st.rerun()

st.markdown("---")

if st.session_state["mensaje_exito_temp"]:
    st.success(st.session_state["mensaje_exito_temp"])
    st.session_state["mensaje_exito_temp"] = None

# ==========================================
# 7. SECCIONES MODULARIZADAS (VISTAS)
# ==========================================

def vista_inicio():
    st.markdown("<h2 class='main-title'>🏢 Centro de Mando VSP - Gobernación de Sucre</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Dashboard Ejecutivo de Control y Alertas en Tiempo Real</p>", unsafe_allow_html=True)
    
    hoy = datetime.today().date()
    
    # Cargar datos para KPIs
    df_meta = cargar_datos('Eventos')
    df_cv = cargar_datos('Compromisos')
    df_ips = cargar_datos('IPS_UPGD')
    df_casos = cargar_datos('Casos_Criticos')
    df_muestras = cargar_datos('Muestras_Lab')
    df_riesgos = cargar_datos('Riesgos_VSP')
    
    # Inyectar Cumpleaños y Validar si hay hoy
    df_cump = cargar_datos('Cumpleanos')
    if not df_cump.empty:
        cumpleaneros_hoy = []
        hoy_str = hoy.strftime("%m-%d")
        eventos_cumple = []
        
        for _, row in df_cump.iterrows():
            f_nac = str(row['Fecha_Nacimiento'])
            if f_nac == hoy_str:
                cumpleaneros_hoy.append(row['Funcionario'])
                
            try:
                mes, dia = f_nac.split('-')
                fecha_evento = datetime(hoy.year, int(mes), int(dia)).strftime("%Y-%m-%d")
                eventos_cumple.append({
                    'Fecha': fecha_evento,
                    'Hora Inicio': '08:00',
                    'Hora Fin': '17:00',
                    'Responsable': row['Funcionario'],
                    'Tipo de Evento': '🎂 CUMPLEAÑOS',
                    'Municipio': 'Sede Departamental',
                    'Lugar': 'Oficina VSP',
                    'Vehículo': 'No',
                    'Estado': 'Confirmado',
                    'Observaciones': 'Celebración'
                })
            except Exception:
                pass
                
        if eventos_cumple:
            df_eventos_cump = pd.DataFrame(eventos_cumple)
            if df_meta.empty:
                df_meta = df_eventos_cump
            else:
                df_meta = pd.concat([df_meta, df_eventos_cump], ignore_index=True)
                
        if cumpleaneros_hoy:
            st.balloons()
            nombres = ", ".join(cumpleaneros_hoy)
            st.markdown(f"<div style='background-color: #ffdeeb; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4785; margin-bottom: 20px;'><h2 style='color: #ff4785; margin:0;'>🎉 ¡Feliz Cumpleaños! 🎂</h2><h4 style='color: #333; margin:0;'>Hoy celebramos el cumpleaños de: <b>{nombres}</b></h4></div>", unsafe_allow_html=True)
    
    # Calcular KPIs
    # 1. Silencio Epi
    ips_silencio = len(df_ips[df_ips['Reporto_Ultima_Semana'] == "No"]) if not df_ips.empty else 0
    total_ips = len(df_ips) if not df_ips.empty else 0
    
    # 2. Casos Críticos en Mora
    try:
        if not df_casos.empty:
            df_casos["Dias_Mora"] = pd.to_numeric(df_casos["Dias_Mora"], errors='coerce').fillna(0)
            casos_mora = len(df_casos[(df_casos["Fase"] != "Unidad de Análisis Cerrada") & (df_casos["Dias_Mora"] > 7)])
        else:
            casos_mora = 0
    except Exception:
        casos_mora = 0
        
    # 3. Compromisos
    comp_totales = len(df_cv) if not df_cv.empty else 0
    if comp_totales > 0:
        comp_cumplidos = len(df_cv[df_cv["Estado"].astype(str).str.contains("CUMPLIDO|FINALIZADO", case=False, na=False)])
        porc_cumplimiento = int((comp_cumplidos / comp_totales) * 100)
    else:
        porc_cumplimiento = 100
        
    # 4. Muestras en Mora
    try:
        muestras_mora = len(df_muestras[(df_muestras["Estado"] == "Enviada / Pendiente") & (pd.to_numeric(df_muestras["Dias_Espera"], errors='coerce') > 5)]) if not df_muestras.empty else 0
    except Exception:
        muestras_mora = 0
        
    # 5. Riesgos Extremos Activos
    try:
        if not df_riesgos.empty:
            riesgos_activos = df_riesgos[df_riesgos['Estado'] != "Cerrado/Controlado"]
            riesgos_extremos = len(riesgos_activos[riesgos_activos['Nivel_Riesgo'].str.contains("Extremo", na=False)])
        else:
            riesgos_extremos = 0
    except Exception:
        riesgos_extremos = 0
    
    # Mostrar KPIs
    st.markdown("### 📊 Panel de Alertas Globales")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f"<div class='metric-card' style='border-left: 5px solid #ef4444;'>⚠️ <b>Silencio Epi</b><h2 style='color:#ef4444; margin:0;'>{ips_silencio} <span style='font-size:1rem; color:#94a3b8;'>/ {total_ips}</span></h2><small>Clínicas sin reporte</small></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card' style='border-left: 5px solid #f97316;'>🚨 <b>Casos Críticos</b><h2 style='color:#f97316; margin:0;'>{casos_mora}</h2><small>En mora > 7 días</small></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card' style='border-left: 5px solid #b91c1c;'>🔴 <b>Riesgos Ext.</b><h2 style='color:#b91c1c; margin:0;'>{riesgos_extremos}</h2><small>Amenazas críticas</small></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card' style='border-left: 5px solid #10b981;'>✅ <b>Gestión Téc.</b><h2 style='color:#10b981; margin:0;'>{porc_cumplimiento}%</h2><small>Compromisos listos</small></div>", unsafe_allow_html=True)
    c5.markdown(f"<div class='metric-card' style='border-left: 5px solid #3b82f6;'>🧪 <b>Laboratorio</b><h2 style='color:#3b82f6; margin:0;'>{muestras_mora}</h2><small>Muestras retrasadas</small></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- METRICAS DEL CALENDARIO RESTAURADAS ---
    if not df_meta.empty:
        df_meta["Fecha_DT"] = pd.to_datetime(df_meta["Fecha"], errors='coerce')
        df_ua = df_meta[(df_meta["Lugar"] == "UNIDAD DE ANALISIS") | (df_meta["Tipo de Evento"] == "UNIDAD DE ANALISIS")]
        ua_vig = len(df_ua[df_ua["Fecha_DT"].dt.date >= hoy])
        ua_ven = len(df_ua[df_ua["Fecha_DT"].dt.date < hoy])
        sala_mes = len(df_meta[(df_meta["Lugar"] == "Sala Situacional") & (df_meta["Fecha_DT"].dt.month == hoy.month)])
        veh_hoy = len(df_meta[(df_meta["Fecha"].astype(str) == hoy.strftime("%Y-%m-%d")) & (df_meta["Vehículo"] == "Sí")])
    else:
        ua_vig = ua_ven = sala_mes = veh_hoy = 0

    st.markdown("### 📅 Programación y Eventos (Calendario)")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.markdown(f"<div class='metric-card'>📌 <b>Total Actividades</b><h3>{len(df_meta)}</h3></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card'>📅 <b>Actividades Hoy</b><h3>{len(df_meta[df_meta['Fecha'].astype(str).str.startswith(hoy.strftime('%Y-%m-%d'))]) if not df_meta.empty else 0}</h3></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card'>🏢 <b>Sala Situacional</b><h3>{sala_mes} Prog.</h3></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-card'>🧬 <b>U. Análisis</b><h3>{len(df_ua) if not df_meta.empty else 0} Total</h3><small>🟢 {ua_vig} Vig | 🔴 {ua_ven} Ven</small></div>", unsafe_allow_html=True)
    m5.markdown(f"<div class='metric-card'>🚗 <b>Con Vehículo</b><h3>{veh_hoy} Hoy</h3></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # --------------------------------------------
    
    # Layout de resumen inferior
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("#### 📅 Actividades de Campo Hoy")
        if not df_meta.empty:
            df_hoy = df_meta[df_meta['Fecha'].astype(str).str.startswith(hoy.strftime('%Y-%m-%d'))]
            if not df_hoy.empty:
                for idx, r in df_hoy.iterrows():
                    st.info(f"**{r['Tipo de Evento']}** en {r['Municipio']} (Responsable: {r['Responsable']})")
            else:
                st.success("No hay actividades de campo programadas para hoy.")
        else:
            st.success("No hay actividades de campo programadas para hoy.")
                
    with c_right:
        st.markdown("#### 🏘️ Vigilancia Comunitaria Activa")
        df_vbc = cargar_datos("VBC_Rumores")
        if not df_vbc.empty:
            rumores_activos = len(df_vbc[df_vbc["Estado_Verificacion"].astype(str).str.contains("Pendiente", case=False, na=False)])
            st.warning(f"**{rumores_activos}** rumores comunitarios pendientes de verificación oficial.")
        else:
            st.info("No hay rumores comunitarios registrados.")
            
    st.markdown("---")

    st.markdown("### 🚀 Accesos Directos de la Red")
    col_ad1, col_ad2, col_ad3, col_ad4, col_ad5 = st.columns(5)
    with col_ad1:
        st.link_button("🌐 Portal SIVIGILA 4.0", ENLACE_PORTAL_WEB, use_container_width=True)
    with col_ad2:
        st.link_button("📞 Directorio Externo (Drive)", URL_DIRECTORIO_ENTIDADES, use_container_width=True)
    with col_ad3:
        if st.button("🎥 Solicitudes Virtuales (Teams/Forms)", use_container_width=True):
            st.session_state["seccion_actual"] = "🛠️ Enlaces y Solicitudes HC"
            st.rerun()
    with col_ad4:
        if st.button("🚨 Alertas y Notificaciones", use_container_width=True):
            st.session_state["seccion_actual"] = "🚨 Alertas e Inventario"
            st.rerun()
    with col_ad5:
        st.link_button("🔢 Consecutivo de Actas (Drive)", URL_CONSECUTIVOS, use_container_width=True)
        
    col_ext1, col_ext2, col_ext3 = st.columns([2, 2, 2])
    with col_ext1:
        st.link_button("🏛️ Secretaría de Salud de Sucre (VSP)", "https://www.saludsucre.gov.co/tema/vigilancia-salud-publica", use_container_width=True)
    with col_ext2:
        st.link_button("📰 Repositorio de Boletines (SIVIGILA)", "https://drive.google.com/drive/folders/1lRj3ywE0y7sbMYwkT7m2QOcNk3JaYCEb?usp=sharing", use_container_width=True)
    with col_ext3:
        rol_actual = st.session_state.get("rol_conectado", "")
        if rol_actual in ["Administrador Total", "Líder", "Lider", "Coordinador"]:
            st.link_button("📂 Drive Interno de Actividades", "https://drive.google.com/drive/folders/1G21HXwnRNO0uxmTfplBpD8abfDlV3fxl?usp=sharing_eil&ts=6978d2df", use_container_width=True)
            
    st.divider()

    st.markdown("### 🔍 Panel de Filtros Cruzados (Agenda Mensual)")
    f_col1, f_col2, f_col3 = st.columns(3)
    
    lista_opciones_lugar = ["Mostrar todos los espacios", "Sala Situacional"]
    if not df_meta.empty:
        lista_opciones_lugar.extend(sorted([str(l) for l in df_meta["Lugar"].unique() if l and str(l).strip() not in ["", "Sala Situacional"]]))
    lugar_sel = f_col1.selectbox("Filtrar por Espacio/Lugar:", lista_opciones_lugar)
    
    lista_opciones_resp = ["Mostrar todos los responsables"]
    if not df_meta.empty:
        lista_opciones_resp.extend(sorted([str(r) for r in df_meta["Responsable"].unique() if r]))
    resp_sel = f_col2.selectbox("Filtrar por Responsable:", lista_opciones_resp)
    
    lista_opciones_mun = ["Mostrar todos los municipios"]
    if not df_meta.empty:
        lista_opciones_mun.extend(sorted([str(m) for m in df_meta["Municipio"].unique() if m]))
    mun_sel = f_col3.selectbox("Filtrar por Municipio:", lista_opciones_mun)

    df_eventos_cal = df_meta.copy() if not df_meta.empty else pd.DataFrame()
    if not df_eventos_cal.empty:
        if lugar_sel != "Mostrar todos los espacios": df_eventos_cal = df_eventos_cal[df_eventos_cal["Lugar"] == lugar_sel]
        if resp_sel != "Mostrar todos los responsables": df_eventos_cal = df_eventos_cal[df_eventos_cal["Responsable"] == resp_sel]
        if mun_sel != "Mostrar todos los municipios": df_eventos_cal = df_eventos_cal[df_eventos_cal["Municipio"] == mun_sel]

    st.markdown("### 🗓️ Calendario Institucional Principal")
    eventos_list = []
    
    # Marcar festivos en el calendario
    import holidays
    co_holidays = holidays.CO(years=hoy.year)
    for festivo_date, festivo_name in co_holidays.items():
        eventos_list.append({
            "title": f"🎉 {festivo_name}",
            "start": festivo_date.strftime("%Y-%m-%d"),
            "display": "background",
            "backgroundColor": "rgba(239, 68, 68, 0.2)"
        })

    if not df_eventos_cal.empty:
        for _, r in df_eventos_cal.iterrows():
            tipo_ev_upper = str(r["Tipo de Evento"]).upper()
            if "UNIDAD DE ANALISIS" in tipo_ev_upper or r["Lugar"] == "UNIDAD DE ANALISIS": color = "#9b59b6"
            elif "CAPACITACION" in tipo_ev_upper: color = "#e67e22"
            elif r["Lugar"] == "Sala Situacional": color = "#2ecc71"
            elif r["Lugar"] == "Auditorio Panzigua": color = "#34495e"
            else: color = "#36a2eb"
            
            v_emoji = " 🚗" if r["Vehículo"] == "Sí" else ""
            hora_limpia = formatear_hora_12h(r['Hora Inicio'])
            encabezado_lugar = "🏢 SALA" if r["Lugar"] == "Sala Situacional" else "🎭 AUDITORIO" if r["Lugar"] == "Auditorio Panzigua" else f"📍 {r['Tipo de Evento']}"
            titulo_completo = f"{encabezado_lugar} | ⏰ {hora_limpia} - {r['Tipo de Evento']} | 👥 {r['Responsable']} ({r['Municipio']}){v_emoji}"
            
            eventos_list.append({
                "title": titulo_completo,
                "start": f"{r['Fecha']}T{r['Hora Inicio']}:00",
                "end": f"{r['Fecha']}T{r['Hora Fin']}:00",
                "backgroundColor": color, "borderColor": color
            })
    
    st.markdown("<div style='background: rgba(30,41,59,0.3); padding:20px; border-radius:16px;'>", unsafe_allow_html=True)
    css_calendar = """
    .fc-event-title {
        white-space: normal !important;
        overflow: hidden;
        font-size: 0.85em;
        padding: 2px;
    }
    .fc-event-time {
        display: none !important;
    }
    """
    opciones_cal = {
        "locale": "es", 
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek"},
        "dayMaxEvents": True
    }
    interaccion_cal = calendar(events=eventos_list, options=opciones_cal, custom_css=css_calendar, key="cal_vsp_interactivo")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if interaccion_cal:
        if "eventClick" in interaccion_cal: st.session_state["fecha_seleccionada"] = interaccion_cal["eventClick"]["event"]["start"].split("T")[0]
        elif "dateClick" in interaccion_cal: st.session_state["fecha_seleccionada"] = interaccion_cal["dateClick"]["date"].split("T")[0]

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🛡️ Ver Equipo de Disponibilidad de la Semana Actual", expanded=False):
        lunes = hoy - timedelta(days=hoy.weekday())
        df_d = cargar_datos('Disponibilidad')
        reg_sem = df_d[df_d["Semana_Inicio"] == lunes.strftime("%Y-%m-%d")] if not df_d.empty else pd.DataFrame()
        
        if not reg_sem.empty:
            st.markdown("**🔹 Vigilancia (Sala de Análisis):**")
            integrantes = [i for i in str(reg_sem.iloc[0]["Integrantes"]).split(";") if i.strip()]
            cargos = [c for c in str(reg_sem.iloc[0]["Cargos"]).split(";") if c.strip()]
            cols_disp = st.columns(len(integrantes))
            for i, nombre in enumerate(integrantes):
                cols_disp[i].info(f"👤 **{nombre}** \n*{cargos[i] if i < len(cargos) else 'Asignado'}*")
            lab_resp = str(reg_sem.iloc[0]["Laboratorio_Responsable"]).strip()
            lab_cargo = str(reg_sem.iloc[0]["Laboratorio_Cargo"]).strip()
            if lab_resp and lab_resp not in ["nan", ""]:
                st.markdown("**🔬 Laboratorio de Salud Pública:**")
                st.success(f"🧫 **{lab_resp}** \n*{lab_cargo if lab_cargo else 'Apoyo Analítico'}*")
        else: 
            st.warning("⚠️ Sin equipo de turno asignado para esta semana.")

    st.markdown("---")
    c_tit_abajo, c_btn_exp = st.columns([3, 1])
    c_tit_abajo.subheader(f"🔍 Agenda Operativa del Día: {st.session_state['fecha_seleccionada']}")
    
    if not df_eventos_cal.empty:
        output_stream = io.BytesIO()
        with pd.ExcelWriter(output_stream, engine='openpyxl') as writer:
            df_eventos_cal.to_excel(writer, index=False, sheet_name='Agenda_Filtrada')
        if st.session_state["rol_conectado"] != "Consulta / Invitado":
            c_btn_exp.download_button(label="📥 Exportar Agenda Filtrada", data=output_stream.getvalue(), file_name=f"agenda_filtrada_{hoy.strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    df_filtrado_dia = df_eventos_cal[df_eventos_cal["Fecha"].astype(str) == st.session_state["fecha_seleccionada"]] if not df_eventos_cal.empty else pd.DataFrame()
    if not df_filtrado_dia.empty:
        for _, fila in df_filtrado_dia.sort_values(by="Hora Inicio").iterrows():
            transporte = "🚗 Requiere Vehículo Institucional" if fila["Vehículo"] == "Sí" else "🚶 Desplazamiento Autónomo / Sin Vehículo"
            st.markdown(f"""
            <div class='custom-card'>
                <h4 style='margin:0px; color:#38bdf8;'>⏰ {fila['Hora Inicio']} - {fila['Hora Fin']} | {fila['Tipo de Evento']}</h4>
                <p style='margin:4px 0px;'>👤 <b>Responsable:</b> {fila['Responsable']} | 📍 <b>Lugar:</b> {fila['Lugar']} ({fila['Municipio']})</p>
                <p style='margin:4px 0px; color:#cbd5e1;'><b>Observaciones:</b> {fila['Observaciones'] if fila['Observaciones'] else 'Ninguna'}</p>
                <p style='margin:4px 0px; font-size:0.9em; color:#a7f3d0;'><b>Logística VSP:</b> {transporte}</p>
            </div>
            """, unsafe_allow_html=True)
    else: 
        st.info("🟢 No existen actividades técnicas programadas para la fecha seleccionada.")

def vista_registrar_actividad():
    st.markdown("### 📝 Formulario de Registro de Eventos")
    with st.form("form_reg", clear_on_submit=False):
        f_fecha = st.date_input("Fecha", value=datetime.today())
        c_h1, c_h2 = st.columns(2)
        f_hi = c_h1.time_input("Hora Inicio", value=time(8, 0))
        f_hf = c_h2.time_input("Hora Fin", value=time(10, 0))
        f_resp = st.selectbox("Responsable Técnico", LISTA_RESPONSABLES)
        f_tipo = st.selectbox("Tipo de Evento", LISTA_TIPOS_EVENTO)
        f_mun = st.selectbox("Municipio Destino", LISTA_MUNICIPIOS)
        f_lugar = st.selectbox("Espacio Físico / Lugar", LISTA_LUGARES)
        f_veh = st.toggle("¿Requiere Vehículo para Desplazamiento Territorial?")
        f_obs = st.text_area("Observaciones del Evento")
        btn_guardar = st.form_submit_button("💾 Agendar y Guardar Actividad")

    if btn_guardar:
        import holidays
        co_holidays = holidays.CO(years=f_fecha.year)
        
        hi_str, hf_str = f_hi.strftime("%H:%M"), f_hf.strftime("%H:%M")
        
        if f_fecha.weekday() >= 5:
            st.error("❌ Operación Denegada: El sistema tiene bloqueado el agendamiento para fines de semana (Sábados y Domingos).")
        elif f_fecha in co_holidays:
            st.error(f"❌ Operación Denegada: El día {f_fecha.strftime('%d/%m/%Y')} es festivo ({co_holidays.get(f_fecha)}). No se permite agendar actividades en días feriados.")
        elif f_hi >= f_hf: 
            st.error("🚨 Error de consistencia horaria: La 'Hora Fin' debe ser estrictamente posterior a la 'Hora Inicio'.")
        elif "Seleccione..." in [f_resp, f_mun, f_lugar]: 
            st.error("❌ Faltan campos obligatorios por seleccionar.")
        else:
            cruce_espacio, cruce_responsable = False, False
            eventos_cal = cargar_datos('Eventos')
            if not eventos_cal.empty:
                for _, e in eventos_cal.iterrows():
                    if str(e["Fecha"]) == f_fecha.strftime("%Y-%m-%d"):
                        if hi_str < str(e["Hora Fin"]) and hf_str > str(e["Hora Inicio"]):
                            if f_lugar in ["Sala Situacional", "Auditorio Panzigua"] and e["Lugar"] == f_lugar: cruce_espacio = True
                            if e["Responsable"] == f_resp: cruce_responsable = True
            if cruce_espacio: 
                st.error(f"🚨 Conflicto logístico: El espacio '{f_lugar}' ya se encuentra ocupado en la franja horaria seleccionada.")
            elif cruce_responsable: 
                st.error(f"👤 Conflicto de agenda: El funcionario {f_resp} ya tiene asignada otra actividad en este mismo horario.")
            else:
                nuevo = pd.DataFrame([{"Fecha": f_fecha.strftime("%Y-%m-%d"), "Hora Inicio": hi_str, "Hora Fin": hf_str, "Responsable": f_resp, "Tipo de Evento": f_tipo, "Municipio": f_mun, "Lugar": f_lugar, "Vehículo": "Sí" if f_veh else "No", "Estado": "Programado", "Observaciones": f_obs}])
                guardar_datos(pd.concat([eventos_cal, nuevo], ignore_index=True), 'Eventos')
                st.session_state["mensaje_exito_temp"] = "🎉 ¡Actividad registrada y sincronizada exitosamente!"
                st.session_state["seccion_actual"] = "🏠 Inicio"; st.rerun()

def vista_disponibilidad_semanal():
    st.markdown("### 🛡️ Equipo de Disponibilidad por Semana Epidemiológica (S.E.)")
    hoy_dt = datetime.today()
    semana_actual_epi = obtener_semana_epidemiologica(hoy_dt)
    st.markdown(f'<div style="padding:12px; border-radius:10px; background-color:rgba(14, 116, 144, 0.2); border-left: 5px solid #06b6d4; margin-bottom:20px;"><h4 style="margin:0px; color:#22d3ee;">... SEMANA EPIDEMIOLÓGICA ACTUAL: S.E. {semana_actual_epi}</h4></div>', unsafe_allow_html=True)

    df_d = cargar_datos('Disponibilidad')
    
    # Restringir pestañas de configuración a los roles que no son administradores totales
    if st.session_state["rol_conectado"] == "Administrador Total" or "🛡️ Disponibilidad Semanal" in st.session_state.get("permisos_conectado", []):
        tab_cons, tab_adm, tab_cal = st.tabs(["🔍 Consultar Planificación de Turnos", "🔐 Panel de Configuración", "📅 Calendario Visual"])
    else:
        tab_cons, tab_cal = st.tabs(["🔍 Consultar Planificación de Turnos", "📅 Calendario Visual"])
        tab_adm = None

    semanas_lista = []
    anio_actual = datetime.today().year
    for m in range(1, 13): semanas_lista.extend(generar_semanas_del_mes(anio_actual, m))
    semanas_lista = sorted(list(set(semanas_lista)), key=lambda x: x[0])
    opciones_futuras = [f"S.E. {w[2]} (Del {w[0].strftime('%d/%m/%Y')} al {w[1].strftime('%d/%m/%Y')})" for w in semanas_lista]
    index_actual = next((idx for idx, w in enumerate(semanas_lista) if w[2] == semana_actual_epi), 0)

    with tab_cons:
        semana_consulta = st.selectbox("Seleccione una semana para verificar personal disponible:", opciones_futuras, index=index_actual)
        if semana_consulta:
            sem_sel = semanas_lista[opciones_futuras.index(semana_consulta)]
            reg_sem_sel = df_d[df_d["Semana_Inicio"] == sem_sel[0].strftime("%Y-%m-%d")] if not df_d.empty else pd.DataFrame()
            if not reg_sem_sel.empty:
                st.markdown(f"#### 🛡️ Equipo Asignado para la **S.E. {sem_sel[2]}**")
                integrantes = [i for i in str(reg_sem_sel.iloc[0]["Integrantes"]).split(";") if i.strip()]
                cargos = [c for c in str(reg_sem_sel.iloc[0]["Cargos"]).split(";") if c.strip()]
                if integrantes:
                    cols = st.columns(len(integrantes))
                    for i, nombre in enumerate(integrantes): 
                        cols[i].info(f"👤 **{nombre}**\n\n💼 *{cargos[i] if i < len(cargos) else 'Asignado'}*")
                lab_resp, lab_cargo = str(reg_sem_sel.iloc[0]["Laboratorio_Responsable"]).strip(), str(reg_sem_sel.iloc[0]["Laboratorio_Cargo"]).strip()
                if lab_resp and lab_resp not in ["nan", ""]:
                    st.markdown("**🔬 Laboratorio de Salud Pública (LSP):**")
                    st.success(f"🧫 **{lab_resp}** \n*{lab_cargo if lab_cargo else 'Apoyo Analítico'}*")
            else:
                st.info("No se han estructurado turnos para la semana epidemiológica seleccionada.")

    if tab_adm is not None:
        with tab_adm:
            semana_registro = st.selectbox("Semana epidemiológica a estructurar:", opciones_futuras, index=index_actual, key="reg_sem_combo")
            lunes_reg_str = semanas_lista[opciones_futuras.index(semana_registro)][0].strftime("%Y-%m-%d")
            lista_pre_integrantes, lista_pre_cargos, val_pre_lab_nombre, val_pre_lab_cargo = [], [], "", "Coordinador de Enlace LSP"
            
            if not df_d.empty:
                reg_existente = df_d[df_d["Semana_Inicio"] == lunes_reg_str]
                if not reg_existente.empty:
                    lista_pre_integrantes = [i.strip() for i in str(reg_existente.iloc[0]["Integrantes"]).split(";") if i.strip()]
                    lista_pre_cargos = [c.strip() for c in str(reg_existente.iloc[0]["Cargos"]).split(";") if c.strip()]
                    val_pre_lab_nombre, val_pre_lab_cargo = str(reg_existente.iloc[0]["Laboratorio_Responsable"]), str(reg_existente.iloc[0]["Laboratorio_Cargo"])

            num_integrantes = st.number_input("¿Cuántos integrantes asignará para Vigilancia? (Máx 9):", min_value=1, max_value=9, value=int(len(lista_pre_integrantes) if lista_pre_integrantes else 2))
            int_nombres, int_cargos = [], []
            cols_inputs = st.columns(3)
            for x in range(int(num_integrantes)):
                with cols_inputs[x % 3]:
                    indice_previo = LISTA_RESPONSABLES.index(lista_pre_integrantes[x]) if x < len(lista_pre_integrantes) and lista_pre_integrantes[x] in LISTA_RESPONSABLES else 0
                    nom = st.selectbox(f"Funcionario {x+1}:", LISTA_RESPONSABLES, index=indice_previo, key=f"f_p_{x}")
                    car = st.text_input(f"Cargo / Rol {x+1}:", value=lista_pre_cargos[x] if x < len(lista_pre_cargos) else "Profesional Universitario VSP", key=f"c_p_{x}")
                    if nom != "Seleccione...": 
                        int_nombres.append(nom); int_cargos.append(car)
            
            txt_lab_nom = st.text_input("Responsable de Laboratorio de Salud Pública:", value=val_pre_lab_nombre)
            txt_lab_car = st.text_input("Cargo / Rol de Laboratorio:", value=val_pre_lab_cargo)
            
            if st.button("💾 Guardar Estructura de Turno"):
                if len(int_nombres) != len(set(int_nombres)): 
                    st.error("🚨 Asignación Inválida: No se puede registrar al mismo funcionario más de una vez en el mismo equipo.")
                else:
                    if not df_d.empty: 
                        df_d = df_d[df_d["Semana_Inicio"] != lunes_reg_str]
                    nuevo_turno = pd.DataFrame([{"Semana_Inicio": lunes_reg_str, "Integrantes": ";".join(int_nombres), "Cargos": ";".join(int_cargos), "Laboratorio_Responsable": txt_lab_nom.strip(), "Laboratorio_Cargo": txt_lab_car.strip()}])
                    guardar_datos(pd.concat([df_d, nuevo_turno], ignore_index=True), 'Disponibilidad')
                    st.session_state["mensaje_exito_temp"] = "🎉 ¡Turno epidemiológico publicado exitosamente!"
                    st.rerun()

    with tab_cal:
        st.markdown("### 🗓️ Visualización Mensual de Actividades")
        st.caption("Resumen gráfico de todas las actividades, comités y BAI programadas en el sistema.")
        df_eventos_cal = cargar_datos('Eventos')
        try:
            from streamlit_calendar import calendar
            
            eventos_lista = []
            if not df_eventos_cal.empty:
                for idx, row in df_eventos_cal.iterrows():
                    color = "#3b82f6"
                    if "Comité" in row["Tipo de Evento"] or "Brote" in row["Tipo de Evento"]: color = "#ef4444"
                    elif "BAI" in row["Tipo de Evento"]: color = "#eab308"
                    elif "Capacitación" in row["Tipo de Evento"]: color = "#10b981"
                    
                    try:
                        if pd.api.types.is_datetime64_any_dtype(row['Fecha']):
                            fecha_str = row['Fecha'].strftime('%Y-%m-%d')
                        else:
                            fecha_str = str(row['Fecha']).split(" ")[0]
                            
                        # Format times to HH:MM:SS if needed
                        h_inicio = str(row['Hora Inicio']).strip()
                        if len(h_inicio) == 5: h_inicio += ":00"
                        
                        h_fin = str(row['Hora Fin']).strip()
                        if len(h_fin) == 5: h_fin += ":00"
                        
                        start_time = f"{fecha_str}T{h_inicio}"
                        end_time = f"{fecha_str}T{h_fin}"
                        
                        eventos_lista.append({
                            "title": f"{row['Tipo de Evento']} - {row['Municipio']}",
                            "start": start_time,
                            "end": end_time,
                            "color": color,
                        })
                    except Exception:
                        pass
            
            cal_options = {
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek"
                },
                "initialView": "dayGridMonth",
                "dayMaxEvents": True
            }
            
            css_cal2 = """
            .fc-event-title { white-space: normal !important; overflow: hidden; font-size: 0.85em; padding: 2px; }
            .fc-event-time { display: none !important; }
            """
            calendar(events=eventos_lista, options=cal_options, custom_css=css_cal2)
        except Exception as e:
            st.warning("No se pudo cargar el calendario gráfico interactivo.")

def vista_compromisos_tecnicos():
    st.markdown("### 📋 Gestión Avanzada de Compromisos Técnicos e Institucionales")
    df_cv = cargar_datos('Compromisos')
    
    # Coordinadores e investigadores pueden editar compromisos, pero borrar es exclusivo del admin
    if st.session_state["rol_conectado"] == "Administrador Total":
        t_matriz, t_crear, t_editar = st.tabs(["📋 Matriz de Seguimiento", "📌 Asignar Nuevo Compromiso", "🔄 Responder / Adjuntar Soporte"])
    else:
        t_matriz, t_crear, t_editar = st.tabs(["📋 Matriz de Seguimiento", "📌 Asignar Nuevo Compromiso", "🔄 Responder / Adjuntar Soporte"])
    
    with t_matriz:
        if not df_cv.empty:
            if st.session_state["rol_conectado"] == "Administrador Total":
                df_mostrar = df_cv.copy()
            else:
                df_mostrar = df_cv[df_cv["Responsable"] == st.session_state["usuario_conectado"]].copy()
                
            if not df_mostrar.empty:
                df_mostrar["Alerta"] = df_mostrar.apply(calcular_semaforo_compromiso, axis=1)
                st.dataframe(df_mostrar[["Fecha_Acuerdo", "Responsable", "Compromiso", "Plazo", "Estado", "Alerta", "Respuesta_Avance"]], use_container_width=True, hide_index=True)
                
                st.markdown("---")
            # st.markdown("#### 💬 Notificar por WhatsApp")
            # st.caption("Envía un recordatorio rápido directo al responsable del compromiso (abre WhatsApp Web/App).")
            
            # # Evitar fallos por emojis usando str.contains
            # pendientes = df_mostrar[df_mostrar["Estado"].astype(str).str.contains("PENDIENTE", case=False, na=False)]
            # if pendientes.empty:
            #     st.success("✅ Todos los compromisos están finalizados. No hay notificaciones pendientes.")
            # else:
            #     for idx, row in pendientes.iterrows():
            #         col1, col2 = st.columns([3, 1])
            #         with col1:
            #             st.markdown(f"**{row['Responsable']}**: {str(row['Compromiso'])[:50]}... (Plazo: {row['Plazo']})")
            #         with col2:
            #             import urllib.parse
            #             cuerpo = urllib.parse.quote(f"Hola {row['Responsable']},\n\nTe escribo desde el sistema VSP para recordarte el siguiente compromiso que se encuentra pendiente o en proceso:\n\n📌 *Tarea:* {row['Compromiso']}\n⏰ *Plazo Máximo:* {row['Plazo']}\n\nPor favor adjuntar los soportes en la plataforma.\n\nGracias.")
            #             wa_link = f"https://wa.me/?text={cuerpo}"
            #             st.markdown(f"<a href='{wa_link}' target='_blank' style='display:inline-block; padding: 5px 10px; background-color: #25D366; color: white; border-radius: 5px; text-decoration: none; font-size: 0.8rem; margin-top: 2px;'>🟩 Enviar WhatsApp</a>", unsafe_allow_html=True)
                        
            st.markdown("---")
            st.markdown("#### 📄 Generador Oficial de Actas (PDF)")
            st.caption("Genera un acta en formato PDF para impresión o firma formal.")
            opciones_pdf = ["Seleccione un compromiso..."] + [f"{idx} - Tarea de {row['Responsable']} ({row['Fecha_Acuerdo']})" for idx, row in df_mostrar.iterrows()]
            comp_pdf_sel = st.selectbox("Seleccione el compromiso para generar el acta:", opciones_pdf)
            
            if comp_pdf_sel != "Seleccione un compromiso...":
                idx_pdf = int(comp_pdf_sel.split(" - ")[0])
                row_pdf = df_mostrar.loc[idx_pdf]
                
                titulo = "ACTA DE COMPROMISO INSTITUCIONAL"
                cuerpo = f"En la fecha {row_pdf['Fecha_Acuerdo']}, se establecio el siguiente compromiso de obligatorio cumplimiento para la red de Vigilancia en Salud Publica del departamento:\n\n"
                cuerpo += f"RESPONSABLE ASIGNADO: {row_pdf['Responsable']}\n"
                cuerpo += f"COMPROMISO TECNICO: {row_pdf['Compromiso']}\n"
                cuerpo += f"PLAZO MAXIMO DE ENTREGA: {row_pdf['Plazo']}\n"
                cuerpo += f"ESTADO ACTUAL: {row_pdf['Estado']}\n\n"
                cuerpo += "El funcionario asume la responsabilidad de dar estricto cumplimiento a las tareas encomendadas dentro de los terminos establecidos, de conformidad con los lineamientos del Instituto Nacional de Salud y la Secretaria de Salud."
                
                pdf_data = generar_pdf_oficial(titulo, cuerpo, row_pdf['Responsable'])
                if pdf_data:
                    st.download_button(
                        label="📥 Descargar Acta de Compromiso (PDF)",
                        data=pdf_data,
                        file_name=f"Acta_Compromiso_{str(row_pdf['Responsable']).replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
            
            st.markdown("---")
            st.markdown("#### 📂 Visor de Evidencias / Soportes Oficiales")
            df_con_soporte = df_mostrar[df_mostrar["Ruta_Soporte"] != ""]
            if not df_con_soporte.empty:
                opciones_descarga = [f"{idx} - Tarea de {row['Responsable']} ({row['Fecha_Acuerdo']})" for idx, row in df_con_soporte.iterrows()]
                comp_elegido = st.selectbox("Seleccione soporte digital para descargar:", opciones_descarga)
                if comp_elegido:
                    ruta_archivo = df_con_soporte.loc[int(comp_elegido.split(" - ")[0]), "Ruta_Soporte"]
                    if os.path.exists(ruta_archivo):
                        with open(ruta_archivo, "rb") as f_archivo: 
                            st.download_button(label=f"📥 Documento ({os.path.basename(ruta_archivo)})", data=f_archivo.read(), file_name=os.path.basename(ruta_archivo), use_container_width=True)
            
            if st.session_state["rol_conectado"] == "Administrador Total":
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("🗑️ Depuración de Compromisos (Exclusivo Administrador)"):
                    df_cv_del = df_cv.copy()
                    df_cv_del['ID_Fila'] = range(len(df_cv_del))
                    df_cv_del['Resumen'] = df_cv_del['Fecha_Acuerdo'].astype(str) + " - " + df_cv_del['Responsable'] + " (" + df_cv_del['Compromiso'].str.slice(0, 40) + "...)"
                    
                    opcion_borrar = st.selectbox("Seleccione el compromiso que desea eliminar permanentemente:", ["Seleccione..."] + df_cv_del['Resumen'].tolist())
                    if opcion_borrar != "Seleccione..." and st.button("❌ ELIMINAR COMPROMISO DEFINITIVAMENTE", type="primary"):
                        idx_eliminar = df_cv_del[df_cv_del['Resumen'] == opcion_borrar]['ID_Fila'].values[0]
                        df_final_comp = df_cv.drop(df_cv.index[idx_eliminar])
                        guardar_datos(df_final_comp, 'Compromisos')
                        st.session_state["mensaje_exito_temp"] = "🗑️ Compromiso eliminado correctamente de la base de datos Excel."
                        st.rerun()
        else: 
            st.info("No hay compromisos en la base de datos.")

    with t_crear:
        with st.form("form_comp", clear_on_submit=True):
            f_acuerdo = st.date_input("Fecha del Acuerdo/Acta", value=datetime.today())
            f_compro = st.text_area("Descripción Detallada del Compromiso:")
            f_resp_c = st.selectbox("Funcionario Responsable:", LISTA_RESPONSABLES, key="f_resp_c")
            f_plazo = st.date_input("Fecha Límite de Entrega:", value=datetime.today() + timedelta(days=5))
            btn_crear_c = st.form_submit_button("📌 Registrar Compromiso Técnico")
            
        if btn_crear_c:
            if f_compro.strip() == "" or "Seleccione..." in f_resp_c:
                st.error("❌ Error: La descripción del compromiso y el funcionario responsable son obligatorios.")
            else:
                nuevo_c = pd.DataFrame([{"Fecha_Acuerdo": f_acuerdo.strftime("%Y-%m-%d"), "Compromiso": f_compro, "Responsable": f_resp_c, "Plazo": f_plazo.strftime("%Y-%m-%d"), "Estado": "🔴 PENDIENTE", "Respuesta_Avance": "", "Ruta_Soporte": ""}])
                guardar_datos(pd.concat([df_cv, nuevo_c], ignore_index=True), 'Compromisos')
                st.session_state["mensaje_exito_temp"] = "📌 ¡Compromiso técnico guardado y asignado exitosamente!"
                st.rerun()

    with t_editar:
        if not df_cv.empty:
            comp_editar_list = [f"{idx} - Encomendado a {row['Responsable']} ({row['Fecha_Acuerdo']})" for idx, row in df_cv.iterrows()]
            sel_c_edit = st.selectbox("Seleccione el compromiso a actualizar:", comp_editar_list)
            if sel_c_edit:
                idx_edit = int(sel_c_edit.split(" - ")[0])
                fila_c = df_cv.loc[idx_edit]
                f_estado_edit = st.selectbox("Actualizar Estado Operativo:", ["🔴 PENDIENTE", "🟢 CUMPLIDO / FINALIZADO"])
                ruta_almacenada = str(fila_c.get('Ruta_Soporte', ''))
                
                archivo_cargado = st.file_uploader("Arrastra aquí el soporte digital / Acta firmada:", type=["pdf", "jpg", "png", "docx"]) if f_estado_edit == "🟢 CUMPLIDO / FINALIZADO" else None
                f_avance_edit = st.text_area("Acciones de Avance / Justificación Técnico:", value=str(fila_c['Respuesta_Avance']))
                
                if st.button("💾 Guardar Cambios"):
                    if archivo_cargado is not None:
                        nombre_final_archivo = f"soporte_comp_{idx_edit}.{archivo_cargado.name.split('.')[-1]}"
                        ruta_completa_destino = os.path.join(CARPETA_SOPORTES, nombre_final_archivo)
                        with open(ruta_completa_destino, "wb") as f: 
                            f.write(archivo_cargado.getbuffer())
                        ruta_almacenada = ruta_completa_destino
                    
                    df_cv.at[idx_edit, 'Estado'] = f_estado_edit
                    df_cv.at[idx_edit, 'Respuesta_Avance'] = f_avance_edit
                    df_cv.at[idx_edit, 'Ruta_Soporte'] = ruta_almacenada
                    guardar_datos(df_cv, 'Compromisos')
                    st.session_state["mensaje_exito_temp"] = "🔄 ¡Compromiso técnico actualizado con éxito!"
                    st.rerun()

def vista_enlaces_hc():
    st.markdown("### 🛠️ Herramientas de Gestión Externa e Institucional")
    col_hc, col_gf = st.columns(2)
    with col_hc:
        st.markdown("<div class='tool-container'>", unsafe_allow_html=True)
        st.subheader("📨 Solicitud Oficial de Documentos")
        
        t_nueva_sol, t_hist_sol = st.tabs(["📨 Nueva Solicitud", "📂 Historial y Seguimiento"])
        
        with t_nueva_sol:
            shc_municipio = st.selectbox("Seleccione Municipio:", LISTA_MUNICIPIOS, key="shc_mun")
            shc_tipo_solicitud = st.selectbox("Tipo de Solicitud:", ["Historia Clínica", "Acta de Defunción", "Ficha Epidemiológica", "Resumen de Historia Clínica", "Otro"])
            
            st.markdown("##### 📄 Datos del Paciente")
            st.info("Puedes digitar los datos de un paciente individual, o subir un listado Excel/CSV con múltiples pacientes.")
            shc_archivo_listado = st.file_uploader("📂 Opcional: Subir listado de pacientes (Excel/CSV)", type=["xlsx", "csv"], key="shc_file")
            
            if shc_archivo_listado:
                shc_paciente = "MÚLTIPLES PACIENTES (VER ADJUNTO)"
                shc_tipo_id = "N/A"
                shc_num_id = "N/A"
                st.success(f"Archivo adjunto cargado: {shc_archivo_listado.name}")
            else:
                shc_paciente = st.text_input("Nombre Completo o Iniciales del Paciente:", placeholder="Ej: Juan Perez / J.A.P.M")
                c_p1, c_p2 = st.columns(2)
                shc_tipo_id = c_p1.selectbox("Tipo Doc:", ["C.C.", "T.I.", "R.C.", "P.E.P.", "C.E.", "S.I."])
                shc_num_id = c_p2.text_input("Número ID:")
                
            shc_eapb = st.text_input("EAPB / Aseguradora / Entidad:", placeholder="Ej: Coosalud / Hospital Local")
            c_f1, c_f2 = st.columns(2)
            shc_f_inicio = c_f1.date_input("Atención Desde:", value=datetime.today() - timedelta(days=7))
            shc_f_fin = c_f2.date_input("Atención Hasta:", value=datetime.today())
            shc_motivo = st.text_area("Motivo de la Solicitud:", placeholder="Ej: Ingreso por posible caso de Dengue Grave. Requiere análisis por comité.")
            
            shc_correo_dest = st.text_input("Correo Institucional de Destino:", value=CORREO_DESTINO_HC)
            
            if shc_archivo_listado:
                cuerpo_correo = f"Cordial saludo,\n\nPor medio de la presente se solicita de manera urgente copia de {shc_tipo_solicitud.upper()} del listado de pacientes adjunto a este correo, afiliados/atendidos en {shc_eapb} en el municipio de {shc_municipio}, correspondiente al período del {shc_f_inicio.strftime('%d/%m/%Y')} al {shc_f_fin.strftime('%d/%m/%Y')}.\n\nMOTIVO DE LA SOLICITUD:\n{shc_motivo}\n\nAgradecemos su pronta gestión.\n\nAtentamente,\nSubprograma de Vigilancia en Salud Pública (VSP) - Gobernación de Sucre."
                asunto_correo = f"SOLICITUD URGENTE: {shc_tipo_solicitud.upper()} MÚLTIPLE - {shc_municipio.upper()}"
            else:
                cuerpo_correo = f"Cordial saludo,\n\nPor medio de la presente se solicita de manera urgente copia de {shc_tipo_solicitud.upper()} del paciente {shc_paciente} con identificación {shc_tipo_id} N° {shc_num_id}, afiliado/atendido en {shc_eapb} en el municipio de {shc_municipio}, correspondiente al período del {shc_f_inicio.strftime('%d/%m/%Y')} al {shc_f_fin.strftime('%d/%m/%Y')}.\n\nMOTIVO DE LA SOLICITUD:\n{shc_motivo}\n\nAgradecemos su pronta gestión.\n\nAtentamente,\nSubprograma de Vigilancia en Salud Pública (VSP) - Gobernación de Sucre."
                asunto_correo = f"SOLICITUD URGENTE: {shc_tipo_solicitud.upper()} - {shc_municipio.upper()} ({shc_paciente})"
            
            # El botón solo se habilitará si se escoge municipio y se digita un nombre (o se sube archivo)
            if shc_municipio != "Seleccione..." and shc_paciente.strip() != "": 
                if st.button("🚀 Enviar y Registrar Automáticamente", use_container_width=True, type="primary"):
                    exito, msg_err = enviar_correo_outlook(shc_correo_dest, asunto_correo, cuerpo_correo, adjunto=shc_archivo_listado)
                    if exito:
                        df_sol = cargar_datos('Solicitudes_Externas')
                        nueva_sol = pd.DataFrame([{
                            "Fecha_Solicitud": datetime.today().strftime("%Y-%m-%d"),
                            "Tipo_Solicitud": shc_tipo_solicitud,
                            "Paciente": shc_paciente.upper(),
                            "Identificacion": f"{shc_tipo_id} {shc_num_id}",
                            "EAPB": shc_eapb.upper(),
                            "Municipio": shc_municipio,
                            "Responsable_Solicitud": st.session_state.get("usuario_conectado", "Desconocido"),
                            "Estado": "🔴 PENDIENTE",
                            "Ruta_Documento": ""
                        }])
                        guardar_datos(pd.concat([df_sol, nueva_sol], ignore_index=True), 'Solicitudes_Externas')
                        st.session_state["mensaje_exito_temp"] = "✅ ¡El correo ha sido enviado y la solicitud registrada en el historial!"
                        st.rerun()
                    else:
                        st.error(f"❌ Error al enviar. Verifica la configuración en '.streamlit/secrets.toml'. Detalle: {msg_err}")
                        
        with t_hist_sol:
            df_solicitudes = cargar_datos('Solicitudes_Externas')
            if not df_solicitudes.empty:
                pendientes = len(df_solicitudes[df_solicitudes['Estado'] == '🔴 PENDIENTE'])
                recibidas = len(df_solicitudes[df_solicitudes['Estado'] == '🟢 RECIBIDO'])
                st.markdown(f"**Total Solicitudes:** {len(df_solicitudes)} | **Pendientes:** {pendientes} | **Recibidas:** {recibidas}")
                
                # Resumen visual
                st.dataframe(df_solicitudes[["Fecha_Solicitud", "Tipo_Solicitud", "Paciente", "EAPB", "Estado"]], use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.markdown("#### 🔄 Recepción de Documentos")
                opciones_pacientes = ["Seleccione un paciente..."] + [f"{idx} - {row['Paciente']} ({row['Tipo_Solicitud']} | {row['Estado']})" for idx, row in df_solicitudes.iterrows()]
                paciente_sel = st.selectbox("Seleccione el paciente para adjuntar su historia médica:", opciones_pacientes)
                
                if paciente_sel != "Seleccione un paciente...":
                    idx_p = int(paciente_sel.split(" - ")[0])
                    fila_p = df_solicitudes.loc[idx_p]
                    
                    if fila_p['Estado'] == "🟢 RECIBIDO" and str(fila_p.get('Ruta_Documento', '')) != "":
                        ruta_hc = fila_p['Ruta_Documento']
                        if os.path.exists(ruta_hc):
                            with open(ruta_hc, "rb") as f_hc:
                                st.download_button(f"📥 Descargar {fila_p['Tipo_Solicitud']} (Recibido)", data=f_hc.read(), file_name=os.path.basename(ruta_hc), use_container_width=True)
                        else:
                            st.warning("⚠️ Archivo no encontrado en el servidor físico.")
                    
                    st.markdown("**Cargar Documento Recibido:**")
                    hc_file = st.file_uploader("Adjuntar PDF o Imagen remitida por la EAPB:", type=["pdf", "jpg", "png", "jpeg"], key=f"up_hc_{idx_p}")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    if c_btn2.button("🗑️ Eliminar Solicitud (Prueba)", use_container_width=True):
                        df_solicitudes = df_solicitudes.drop(idx_p)
                        guardar_datos(df_solicitudes, 'Solicitudes_Externas')
                        st.session_state["mensaje_exito_temp"] = "🗑️ Solicitud de prueba eliminada exitosamente."
                        st.rerun()
                        
                    if c_btn1.button("💾 Guardar Documento y Cerrar", use_container_width=True, type="primary"):
                        if hc_file is not None:
                            os.makedirs(CARPETA_SOPORTES, exist_ok=True)
                            nombre_hc = f"HC_{idx_p}_{datetime.today().strftime('%Y%m%d%H%M')}.{hc_file.name.split('.')[-1]}"
                            ruta_final_hc = os.path.join(CARPETA_SOPORTES, nombre_hc)
                            with open(ruta_final_hc, "wb") as f:
                                f.write(hc_file.getbuffer())
                            
                            df_solicitudes.at[idx_p, 'Estado'] = "🟢 RECIBIDO"
                            df_solicitudes.at[idx_p, 'Ruta_Documento'] = ruta_final_hc
                            guardar_datos(df_solicitudes, 'Solicitudes_Externas')
                            st.session_state["mensaje_exito_temp"] = "✅ ¡Documento médico almacenado y solicitud cerrada con éxito!"
                            st.rerun()
                        else:
                            st.error("❌ Por favor adjunta un archivo antes de guardar.")
            else:
                st.info("No hay solicitudes médicas registradas en el historial.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_gf:
        st.markdown("<div class='tool-container'>", unsafe_allow_html=True)
        
        herramienta_sel = st.radio("Selecciona una herramienta:", ["🌐 Asistencia Google Forms", "🎥 Salas Virtuales Teams"], horizontal=True, label_visibility="collapsed")
        
        if herramienta_sel == "🎥 Salas Virtuales Teams":
            st.subheader("🌐 Solicitud de Salas Virtuales (Teams)")
            
            tab_sol_teams, tab_hist_teams = st.tabs(["🎫 Solicitar Sala", "📋 Historial y Enlaces"])
            
            with tab_sol_teams:
                gf_tema = st.text_input("Tema Central de la Reunión/Evento:", placeholder="Ej: Sala Situacional Dengue")
                c_ft1, c_ft2, c_ft3 = st.columns(3)
                gf_fecha = c_ft1.date_input("Fecha Programada del Evento:", value=datetime.today(), key="gf_fecha_v")
                gf_hora_inicio = c_ft2.time_input("Hora de Inicio:", value=datetime.strptime("08:00", "%H:%M").time(), key="gf_hora_v")
                gf_hora_fin = c_ft3.time_input("Hora Final:", value=datetime.strptime("10:00", "%H:%M").time(), key="gf_hora_fin_v")
                gf_resp = st.selectbox("Funcionario Responsable / Ponente:", LISTA_RESPONSABLES, key="gf_resp_v")
                
                st.markdown("---")
                gf_correo_encargado = st.text_input("Correo del Funcionario Encargado de Crear Links:", placeholder="Ej: sistemas@gobernacion.gov.co")
                
                if st.button("🚀 Enviar Solicitud de Sala", use_container_width=True, type="primary"):
                    if "Seleccione..." in [gf_resp] or gf_tema.strip() == "" or gf_correo_encargado.strip() == "":
                        st.error("❌ Por favor completa todos los campos (Tema, Responsable y Correo del Encargado).")
                    else:
                        asunto_teams = f"NUEVA SOLICITUD DE SALA TEAMS: {gf_tema.upper()}"
                        cuerpo_teams = f"Cordial saludo,\n\nSe requiere la programación urgente de una sala virtual de Teams.\n\nDETALLES DEL EVENTO:\n- Tema: {gf_tema}\n- Fecha: {gf_fecha.strftime('%d/%m/%Y')}\n- Horario: {gf_hora_inicio.strftime('%I:%M %p')} a {gf_hora_fin.strftime('%I:%M %p')}\n- Ponente Responsable: {gf_resp}\n\nPor favor ingresar al Sistema VSP, dirigirse a la pestaña de 'Herramientas de Gestión' -> 'Historial y Enlaces', y asignar el link correspondiente a esta solicitud.\n\nAtentamente,\nSistema Automatizado VSP"
                        
                        exito_t, msg_t = enviar_correo_outlook(gf_correo_encargado, asunto_teams, cuerpo_teams)
                        
                        if exito_t:
                            df_teams = cargar_datos('Solicitudes_Teams')
                            nueva_sol_t = pd.DataFrame([{
                                "Fecha_Solicitud": datetime.today().strftime("%Y-%m-%d"),
                                "Fecha_Evento": f"{gf_fecha.strftime('%Y-%m-%d')} ({gf_hora_inicio.strftime('%H:%M')} a {gf_hora_fin.strftime('%H:%M')})",
                                "Tema": gf_tema.upper(),
                                "Responsable_Evento": gf_resp,
                                "Encargado_Links": gf_correo_encargado,
                                "Estado": "🔴 PENDIENTE",
                                "Enlace_Teams": ""
                            }])
                            guardar_datos(pd.concat([df_teams, nueva_sol_t], ignore_index=True), 'Solicitudes_Teams')
                            st.session_state["mensaje_exito_temp"] = "✅ ¡Solicitud enviada al encargado y registrada en el historial!"
                            st.rerun()
                        else:
                            st.error(f"❌ Error al notificar al encargado. Detalle: {msg_t}")
                            
            with tab_hist_teams:
                df_teams = cargar_datos('Solicitudes_Teams')
                if not df_teams.empty:
                    # Mostrar tabla con estado
                    st.dataframe(df_teams[["Fecha_Evento", "Tema", "Responsable_Evento", "Estado"]], use_container_width=True, hide_index=True)
                    
                    # st.markdown("#### 💬 Recordatorio por WhatsApp")
                    # st.caption("Solicita el link de la reunión directamente por WhatsApp a quien corresponda.")
                    
                    # # Evitar fallos por emojis usando str.contains
                    # pendientes_w = df_teams[df_teams["Estado"].astype(str).str.contains("PENDIENTE", case=False, na=False)]
                    # if not pendientes_w.empty:
                    #     for idx, row in pendientes_w.iterrows():
                    #         col1, col2 = st.columns([3, 1])
                    #         with col1:
                    #             st.markdown(f"**{row['Tema']}** ({row['Fecha_Evento']})")
                    #         with col2:
                    #             import urllib.parse
                    #             cuerpo_w = urllib.parse.quote(f"Hola,\n\nTe escribo para solicitar la creación urgente de un enlace de Teams para el evento:\n\n📌 *Tema:* {row['Tema']}\n⏰ *Fecha/Hora:* {row['Fecha_Evento']}\n\nPor favor ingresa al sistema VSP y asígnalo lo más pronto posible.\n\nGracias.")
                    #             wa_link = f"https://wa.me/?text={cuerpo_w}"
                    #             st.markdown(f"<a href='{wa_link}' target='_blank' style='display:inline-block; padding: 5px 10px; background-color: #25D366; color: white; border-radius: 5px; text-decoration: none; font-size: 0.8rem; margin-top: 2px;'>💬 Pedir Link</a>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("#### 🔗 Asignación de Links (Para uso del Encargado)")
                    pendientes_t = df_teams[df_teams["Estado"].astype(str).str.contains("PENDIENTE", case=False, na=False)]
                    if not pendientes_t.empty:
                        opciones_asig = ["Seleccione una solicitud..."] + [f"{idx} - {row['Tema']} ({row['Fecha_Evento']})" for idx, row in pendientes_t.iterrows()]
                        sala_sel = st.selectbox("Seleccione la solicitud para asignarle el link:", opciones_asig)
                        
                        if sala_sel != "Seleccione una solicitud...":
                            idx_sala = int(sala_sel.split(" - ")[0])
                            link_ingresado = st.text_input("Pegue aquí el enlace de Microsoft Teams:")
                            
                            if st.button("💾 Guardar y Asignar Enlace", use_container_width=True):
                                if link_ingresado.strip() == "":
                                    st.error("❌ El enlace no puede estar vacío.")
                                else:
                                    df_teams.at[idx_sala, 'Estado'] = "🟢 ASIGNADO"
                                    df_teams.at[idx_sala, 'Enlace_Teams'] = link_ingresado.strip()
                                    guardar_datos(df_teams, 'Solicitudes_Teams')
                                    st.session_state["mensaje_exito_temp"] = "✅ ¡Enlace de Teams asignado exitosamente!"
                                    st.rerun()
                    else:
                        st.info("✅ No hay salas virtuales pendientes por asignar.")
                        
                    st.markdown("---")
                    st.markdown("#### 📋 Copiar Enlaces Asignados")
                    asignadas_t = df_teams[df_teams["Estado"] == "🟢 ASIGNADO"]
                    if not asignadas_t.empty:
                        for idx, row in asignadas_t.iterrows():
                            st.success(f"**{row['Tema']}** ({row['Fecha_Evento']} | {row['Responsable_Evento']})\n\n🔗 `{row['Enlace_Teams']}`")
                            st.link_button("🌍 Unirse a la Sala", row['Enlace_Teams'], use_container_width=True)
                            
                    if st.session_state["rol_conectado"] == "Administrador Total":
                        st.markdown("<br>", unsafe_allow_html=True)
                        with st.expander("🗑️ Depuración de Salas (Administrador)"):
                            opciones_borrar_t = ["Seleccione una sala para eliminar..."] + [f"{idx} - {row['Tema']} ({row['Fecha_Evento']})" for idx, row in df_teams.iterrows()]
                            sala_a_borrar = st.selectbox("Sala a eliminar:", opciones_borrar_t)
                            if sala_a_borrar != "Seleccione una sala para eliminar...":
                                idx_del_t = int(sala_a_borrar.split(" - ")[0])
                                if st.button("❌ Confirmar Eliminación Definitiva", use_container_width=True):
                                    df_teams_actualizado = df_teams.drop(df_teams.index[idx_del_t])
                                    guardar_datos(df_teams_actualizado, 'Solicitudes_Teams')
                                    st.session_state["mensaje_exito_temp"] = "🗑️ Sala eliminada del historial correctamente."
                                    st.rerun()
                else:
                    st.info("No se han registrado solicitudes de salas virtuales.")
        else:
            st.subheader("🌐 Enlaces para Asistencia de Eventos Virtuales")
            
            tab_generar, tab_historial = st.tabs(["🚀 Generar Nuevo Enlace", "📋 Historial de Enlaces y Descargas"])
            
            with tab_generar:
                gf_evento = st.selectbox("Tipo de Evento Virtual:", LISTA_TIPOS_EVENTO, key="gf_tipo_v2")
                gf_tema = st.text_input("Tema Central del Evento:", placeholder="Ej: SAR Dengue", key="gf_tema_v2")
                gf_resp = st.selectbox("Funcionario Responsable / Ponente:", LISTA_RESPONSABLES, key="gf_resp_v2")
                gf_fecha = st.date_input("Fecha Programada del Evento:", value=datetime.today(), key="gf_fecha_v2")
                
                btn_generar_link = st.button("🚀 Procesar y Guardar en Bitácora", use_container_width=True, type="primary", key="btn_gen_v2")
                
                if btn_generar_link:
                    if "Seleccione..." in [gf_evento, gf_resp] or gf_tema.strip() == "":
                        st.error("❌ Por favor completa todos los campos obligatorios para procesar los enlaces.")
                    else:
                        url_limpia = BASE_GOOGLE_FORMS.split("?")[0]
                        # Generamos un tema único concatenando la fecha, así evitamos cruce de asistencias en Excel
                        tema_unico = f"{gf_tema.upper().strip()} ({gf_fecha.strftime('%d-%m-%Y')})"
                        link_generado = f"{url_limpia}?usp=pp_url&{ID_TEMA_FORM}={urllib.parse.quote(tema_unico)}"
                        
                        df_historial = cargar_datos('Historial_Enlaces')
                        nuevo_registro = pd.DataFrame([{
                            "Fecha_Registro": gf_fecha.strftime("%Y-%m-%d"),
                            "Tipo_Evento": gf_evento,
                            "Tema_Evento": tema_unico,
                            "Responsable_Ponente": gf_resp,
                            "Enlace_Formulario": link_generado
                        }])
                        guardar_datos(pd.concat([df_historial, nuevo_registro], ignore_index=True), 'Historial_Enlaces')
                        
                        st.session_state["mensaje_exito_temp"] = "🎉 ¡Enlace generado con éxito e indexado en la bitácora!"
                        st.rerun()
                        
            with tab_historial:
                df_historial = cargar_datos('Historial_Enlaces')
                if not df_historial.empty:
                    busqueda = st.text_input("🔍 Buscar en la bitácora (Filtra por Tema, Ponente o Tipo):")
                    if busqueda:
                        mask = df_historial.astype(str).apply(lambda col: col.str.contains(busqueda, case=False, na=False)).any(axis=1)
                        df_historial = df_historial[mask]
                    
                    if not df_historial.empty:
                        st.dataframe(df_historial[["Fecha_Registro", "Tipo_Evento", "Tema_Evento", "Responsable_Ponente"]], use_container_width=True, hide_index=True)
                        opciones_combo = ["Seleccione un evento..."] + [f"{idx} - {row['Tema_Evento']} [{row['Fecha_Registro']}]" for idx, row in df_historial.iterrows()]
                        seleccion_registro = st.selectbox("Seleccione un evento para recuperar sus accesos:", opciones_combo)
                        
                        if seleccion_registro != "Seleccione un evento...":
                            idx_h = int(seleccion_registro.split(" - ")[0])
                            fila_h = df_historial.iloc[idx_h]
                            tema_sel_vsp = str(fila_h["Tema_Evento"]).strip()
                            
                            st.markdown("#### 🔗 Enlace para Responder (Compartir)")
                            st.code(fila_h["Enlace_Formulario"], language="markdown")
                            st.link_button("🌍 Abrir Formulario en Línea", fila_h["Enlace_Formulario"], use_container_width=True)
                            
                            st.markdown("---")
                            st.markdown("#### 📥 Enlace de Descarga de Respuestas a Excel")
                            
                            if URL_GOOGLE_SHEET and "docs.google.com/spreadsheets" in URL_GOOGLE_SHEET and URL_GOOGLE_SHEET != "TU_LINK_DE_GOOGLE_SHEETS_AQUI":
                                try:
                                    base_sheet_url = URL_GOOGLE_SHEET.split("/edit")[0]
                                    export_url = f"{base_sheet_url}/export?format=csv"
                                    df_all = pd.read_csv(export_url).fillna("")
                                    
                                    mask = df_all.astype(str).apply(lambda x: x.str.upper().str.contains(tema_sel_vsp.upper())).any(axis=1)
                                    df_filtrado = df_all[mask]
                                    
                                    if not df_filtrado.empty:
                                        st.success(f"✅ ¡Se detectaron {len(df_filtrado)} participantes registrados en la nube!")
                                        with st.expander("👁️ Ver Vista Previa de Asistentes"):
                                            st.dataframe(df_filtrado, use_container_width=True)
                                        df_a_descargar = df_filtrado
                                    else:
                                        st.info(f"ℹ️ Aún no hay respuestas en la nube para '{tema_sel_vsp}'. El botón generará el formato con los encabezados oficiales.")
                                        df_a_descargar = pd.DataFrame(columns=df_all.columns)
                                    
                                    buffer_excel = io.BytesIO()
                                    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as wr:
                                        df_a_descargar.to_excel(wr, index=False, sheet_name='Asistencia_Filtrada')
                                    
                                    st.download_button(
                                        label=f"📥 Descargar Archivo Excel de: {tema_sel_vsp} (.xlsx)",
                                        data=buffer_excel.getvalue(),
                                        file_name=f"asistencias_{tema_sel_vsp.replace(' ', '_')}_{datetime.today().strftime('%Y%m%d')}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )
                                except Exception as e:
                                    st.error(f"Error de conexión con Google Sheets: {e}")
                            else:
                                st.info("⚠️ Para habilitar la descarga automatizada, pegue el link público de su Google Sheet en la constante `URL_GOOGLE_SHEET` (Línea 41).")
                            
                            if st.session_state["rol_conectado"] == "Administrador Total":
                                st.markdown("<br>", unsafe_allow_html=True)
                                with st.expander("🗑️ Depuración de Enlaces (Administrador)"):
                                    if st.button("❌ Confirmar Eliminación Definitiva del Enlace", key=f"btn_del_link_{idx_h}", use_container_width=True):
                                        df_historial_actualizado = df_historial.drop(df_historial.index[idx_h])
                                        guardar_datos(df_historial_actualizado, 'Historial_Enlaces')
                                        st.session_state["mensaje_exito_temp"] = "🗑️ Enlace eliminado de la bitácora correctamente."
                                        st.rerun()
                                        
                    else:
                        st.info("No se encontraron coincidencias para la búsqueda.")
                else:
                    st.info("Bitácora vacía. Genere un nuevo enlace para iniciar el historial.")
                    
            if not df_historial.empty:
                st.markdown("---")
                st.markdown("#### 📄 Exportación para Informe de Empalme")
                st.caption("Genera un reporte consolidado de todos los enlaces estructurados para rendición de cuentas.")
                buffer_empalme = io.BytesIO()
                with pd.ExcelWriter(buffer_empalme, engine='openpyxl') as wr:
                    df_historial.to_excel(wr, index=False, sheet_name='Historial_Asistencias_VSP')
                st.download_button(
                    label="📥 Exportar Historial Completo para Informe de Empalme",
                    data=buffer_empalme.getvalue(),
                    file_name=f"historial_asistencias_empalme_{datetime.today().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        st.markdown("</div>", unsafe_allow_html=True)

def vista_actas_informes():
    st.markdown("### 📄 Módulo Documental de Actas e Informes de Gestión (VSP)")
    df_actas = cargar_datos('Actas')
    df_consec = cargar_datos('Consecutivos_Actas')
    
    t_ver_actas, t_crear_acta, t_consecutivo = st.tabs(["🔍 Historial de Actas Radicadas", "📝 Generar Nueva Acta / Minuta", "🔢 Generador de Consecutivos"])
    
    with t_ver_actas:
        if not df_actas.empty:
            st.dataframe(df_actas, use_container_width=True, hide_index=True)
            st.markdown("---")
            st.markdown("#### 📥 Visualizar / Descargar Acta Radicada")
            fila_sel = st.selectbox("Seleccione acta para descargar su documento o ver su minuta:", range(len(df_actas)), format_func=lambda x: f"Acta {df_actas.iloc[x]['Fecha_Acta']} - {df_actas.iloc[x]['Tipo_Comite']}")
            if fila_sel is not None:
                acta = df_actas.iloc[fila_sel]
                ruta_doc = acta.get("Ruta_Documento", "")
                if pd.notna(ruta_doc) and str(ruta_doc).strip() != "" and os.path.exists(str(ruta_doc)):
                    with open(str(ruta_doc), "rb") as f:
                        st.download_button(label="📥 Descargar Acta Escaneada (Soporte PDF/Word)", data=f.read(), file_name=os.path.basename(str(ruta_doc)), use_container_width=True, type="primary")
                else:
                    st.warning("⚠️ No se adjuntó archivo físico para esta acta. A continuación se muestra la minuta digital.")
                st.text_area("Minuta / Texto para Copiar a Plantilla Institucional:", value=f"ACTA DE REUNIÓN - VSP SUCRE\nFECHA: {acta['Fecha_Acta']}\nINSTANCIA/COMITÉ: {acta['Tipo_Comite']}\nRESPONSABLE: {acta['Responsable_Acta']}\n\nASISTENTES REGISTRADOS:\n{acta['Asistentes']}\n\nDESARROLLO DE LA SESIÓN:\n{acta['Temas']}\n\nCONCLUSIONES Y COMPROMISOS ADOPTADOS:\n{acta['Conclusiones_Compromisos']}", height=250)
        else: 
            st.info("No se registran actas ni minutas institucionales en el sistema.")

    with t_crear_acta:
        with st.form("form_actas", clear_on_submit=True):
            act_fecha = st.date_input("Fecha de Realización:", value=datetime.today())
            act_tipo = st.selectbox("Instancia / Comité / Mesa Técnica:", LISTA_TIPOS_EVENTO)
            act_resp = st.selectbox("Secretario Técnico / Líder del Acta:", LISTA_RESPONSABLES, key="act_resp")
            act_asistentes = st.text_area("Asistentes (Nombre completo, Entidad, Cargo):", placeholder="Ej: Juan Perez (EAPB Coosalud), Ana Diaz (LSP Sucre)")
            act_temas = st.text_area("Desarrollo Técnico de los Temas Tratados:")
            act_conclusiones = st.text_area("Conclusiones Generals y Tareas Específicas:")
            act_soporte = st.file_uploader("Adjuntar Archivo de Acta Escaneada (PDF, Word, etc.):", type=["pdf", "docx", "jpg", "png"])
            
            if st.form_submit_button("💾 Archivar y Registrar Acta Oficial"):
                if "Seleccione..." in act_resp: 
                    st.error("Debe definir un funcionario como Secretario Técnico/Responsable del acta.")
                else:
                    ruta_soporte = ""
                    if act_soporte is not None:
                        os.makedirs(CARPETA_SOPORTES, exist_ok=True)
                        nombre_archivo = f"ACTA_{act_fecha.strftime('%Y%m%d')}_{act_tipo.replace(' ', '_')}.{act_soporte.name.split('.')[-1]}"
                        ruta_soporte = os.path.join(CARPETA_SOPORTES, nombre_archivo)
                        with open(ruta_soporte, "wb") as f:
                            f.write(act_soporte.getbuffer())
                    
                    nueva_acta = pd.DataFrame([{"Fecha_Acta": act_fecha.strftime("%Y-%m-%d"), "Tipo_Comite": act_tipo, "Responsable_Acta": act_resp, "Asistentes": act_asistentes, "Temas": act_temas, "Conclusiones_Compromisos": act_conclusiones, "Ruta_Documento": ruta_soporte}])
                    guardar_datos(pd.concat([df_actas, nueva_acta], ignore_index=True), 'Actas')
                    st.session_state["mensaje_exito_temp"] = "🎉 ¡Acta técnica archivada e indexada con éxito!"
                    st.rerun()

    with t_consecutivo:
        st.markdown("#### 🔢 Generador Automático de Consecutivos Institucionales")
        st.info("Este módulo asigna el siguiente número consecutivo oficial para los documentos de VSP de forma automática y lo bloquea para que no se repita. Incluye validación de fecha.")
        
        c_tipo, c_fecha = st.columns(2)
        tipo_doc_consecutivo = c_tipo.selectbox("Tipo de Documento Oficial:", ["ACTA (Reuniones/Comités)", "CIRCULAR (Interna/Lineamientos)", "MEMORANDO (Interno)", "OFICIO (Interno)", "OTRO (Externo/Recibido)"])
        if st.session_state.get("rol_conectado", "") == "Administrador Total":
            min_val = datetime.today() - timedelta(days=4)
            max_val = datetime.today() + timedelta(days=4)
        else:
            min_val = datetime.today()
            max_val = datetime.today()
            
        fecha_consecutivo = c_fecha.date_input("Fecha del Documento:", value=datetime.today(), min_value=min_val, max_value=max_val)
        
        # Determinar prefijo
        if "ACTA" in tipo_doc_consecutivo: prefijo = "ACTA-VSP"
        elif "CIRCULAR" in tipo_doc_consecutivo: prefijo = "CIRC-VSP"
        elif "MEMO" in tipo_doc_consecutivo: prefijo = "MEMO-VSP"
        elif "OFICIO" in tipo_doc_consecutivo: prefijo = "OFI-VSP"
        else: prefijo = "EXT-VSP"
        
        año_actual = fecha_consecutivo.strftime("%Y")
        
        # Calcular sugerencia automática
        df_filtrado = df_consec[(df_consec['Tipo_Documento'] == tipo_doc_consecutivo) & (df_consec['Fecha'].astype(str).str.startswith(año_actual))]
        if df_filtrado.empty:
            siguiente_numero = 1
        else:
            try:
                numeros = df_filtrado['Consecutivo'].str.split('-').str[-1].astype(int)
                siguiente_numero = numeros.max() + 1
            except:
                siguiente_numero = len(df_filtrado) + 1
        
        consecutivo_sugerido = f"{prefijo}-{año_actual}-{str(siguiente_numero).zfill(3)}"
        
        es_admin = st.session_state.get("rol_conectado") == "Administrador Total"
        label_consec = "Número Consecutivo a Asignar (Modificable solo por Administrador):" if es_admin else "Número Consecutivo Oficial (Asignación Automática):"
        consecutivo_final = st.text_input(label_consec, value=consecutivo_sugerido, disabled=not es_admin)
        asunto_consecutivo = st.text_input("Asunto o Tema Principal del Documento:")
        responsable_consecutivo = st.selectbox("Responsable / Elabora:", LISTA_RESPONSABLES, key="consec_resp")
        
        if st.button("🎯 Generar y Reservar Nuevo Consecutivo", use_container_width=True, type="primary"):
            if "Seleccione..." in responsable_consecutivo or asunto_consecutivo.strip() == "" or consecutivo_final.strip() == "":
                st.error("⚠️ Debe completar el consecutivo, el asunto y el responsable.")
            else:
                nuevo_consec = pd.DataFrame([{
                    "Fecha": fecha_consecutivo.strftime("%Y-%m-%d"),
                    "Tipo_Documento": tipo_doc_consecutivo,
                    "Consecutivo": consecutivo_final.strip().upper(),
                    "Asunto": asunto_consecutivo.upper(),
                    "Responsable": responsable_consecutivo
                }])
                
                df_consec = pd.concat([df_consec, nuevo_consec], ignore_index=True)
                guardar_datos(df_consec, 'Consecutivos_Actas')
                
                st.session_state["mensaje_exito_temp"] = f"✅ ¡Consecutivo {consecutivo_final.strip().upper()} asignado con éxito! Por favor úselo en su documento."
                st.rerun()
        
        st.markdown("---")
        st.markdown("#### 📋 Historial de Consecutivos Asignados")
        if not df_consec.empty:
            st.dataframe(df_consec.sort_values("Fecha", ascending=False), use_container_width=True, hide_index=True)
            
            if st.session_state.get("rol_conectado") == "Administrador Total":
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("🛠️ Depuración de Consecutivos (Solo Administrador)"):
                    st.warning("Use esta opción para borrar registros de prueba o errores de digitación. El número quedará libre de nuevo.")
                    consec_a_borrar = st.selectbox("Seleccione el registro a eliminar:", range(len(df_consec)), format_func=lambda x: f"{df_consec.iloc[x]['Consecutivo']} - {df_consec.iloc[x]['Asunto']}")
                    if st.button("⚠️ Eliminar Registro Definitivamente", use_container_width=True):
                        df_consec = df_consec.drop(consec_a_borrar)
                        guardar_datos(df_consec, 'Consecutivos_Actas')
                        st.session_state["mensaje_exito_temp"] = "🗑️ Registro de consecutivo eliminado exitosamente."
                        st.rerun()
        else:
            st.caption("No hay consecutivos asignados todavía en el sistema.")

def vista_alertas_inventario():
    st.markdown("### 🚨 Central de Alertas Epidemiológicas e Insumos Críticos")
    df_alertas = cargar_datos('Alertas_Inventario')
    t_alertas, t_insumos = st.tabs(["📢 Circulares y Alertas INS/MinSalud", "🧪 Inventario de Contingencia (LSP)"])
    
    with t_alertas:
        st.markdown("#### 📢 Alertas y Lineamientos Nacionales Activos")
        df_solo_alertas = df_alertas[df_alertas["Tipo_Item"] == "CIRCULAR_ALERTA"] if not df_alertas.empty else pd.DataFrame()
        if not df_solo_alertas.empty:
            for _, fila in df_solo_alertas.iterrows():
                color_borde = "#ef4444" if "ALTO" in str(fila["Clasificacion_Riesgo"]).upper() else "#eab308" if "MEDIO" in str(fila["Clasificacion_Riesgo"]).upper() else "#3b82f6"
                st.markdown(f"""
                <div style='padding:12px; border-radius:8px; background-color:rgba(30,41,59,0.5); margin-bottom:10px; border-left:5px solid {color_borde};'>
                    <span style='float:right; font-size:0.85em; background-color:rgba(255,255,255,0.1); padding:3px 8px; border-radius:15px;'>📅 {fila['Fecha_Registro']}</span>
                    <h5 style='margin:0; color:#cbd5e1;'>📢 {fila['Titulo_Nombre']}</h5>
                    <p style='margin:5px 0 0 0; font-size:0.95em; color:#94a3b8;'>{fila['Descripcion_Cantidad']}</p>
                    <small style='color:{color_borde}; font-weight:bold;'>Prioridad de Intervención: {fila['Clasificacion_Riesgo']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar botón de descarga si existe soporte documental
                ruta_doc = fila.get("Ruta_Documento", "")
                if pd.notna(ruta_doc) and str(ruta_doc).strip() != "" and os.path.exists(str(ruta_doc)):
                    with open(str(ruta_doc), "rb") as f:
                        btn_descarga = st.download_button(
                            label="📥 Descargar Circular / Documento Soporte",
                            data=f,
                            file_name=os.path.basename(str(ruta_doc)),
                            key=f"dl_alerta_{_}"
                        )
                st.markdown("<br>", unsafe_allow_html=True)
        else: 
            st.info("No hay circulares epidemiológicas urgentes en el histórico.")
        
        if st.session_state["rol_conectado"] == "Administrador Total" or "🚨 Alertas e Inventario" in st.session_state.get("permisos_conectado", []):
            with st.expander("➕ Difundir Nueva Circular Externa"):
                with st.form("form_alertas", clear_on_submit=True):
                    al_fecha = st.date_input("Fecha Emisión Circular:", value=datetime.today())
                    al_titulo = st.text_input("Número / Título de la Circular:", placeholder="Ej: Circular 014 INS - Alerta de Dengue")
                    al_desc = st.text_area("Lineamientos y Directrices Clave:")
                    al_riesgo = st.select_slider("Prioridad de Respuesta:", options=["Bajo", "Medio", "Alto"])
                    al_archivo = st.file_uploader("Subir Circular (Opcional, PDF):", type=["pdf", "png", "jpg", "jpeg", "docx"])
                    
                    if st.form_submit_button("📢 Publicar y Notificar Alerta"):
                        ruta_final = ""
                        if al_archivo:
                            if not os.path.exists(CARPETA_SOPORTES):
                                os.makedirs(CARPETA_SOPORTES)
                            nombre_safe = f"circular_{datetime.now().strftime('%Y%m%d%H%M%S')}_{al_archivo.name.replace(' ', '_')}"
                            ruta_final = os.path.join(CARPETA_SOPORTES, nombre_safe)
                            with open(ruta_final, "wb") as f:
                                f.write(al_archivo.getbuffer())
                                
                        nueva_a = pd.DataFrame([{
                            "Fecha_Registro": al_fecha.strftime("%Y-%m-%d"), 
                            "Tipo_Item": "CIRCULAR_ALERTA", 
                            "Titulo_Nombre": al_titulo, 
                            "Descripcion_Cantidad": al_desc, 
                            "Clasificacion_Riesgo": al_riesgo.upper(),
                            "Ruta_Documento": ruta_final
                        }])
                        guardar_datos(pd.concat([df_alertas, nueva_a], ignore_index=True), 'Alertas_Inventario')
                        st.session_state["mensaje_exito_temp"] = "📢 ¡Circular epidemiológica difundida!"
                        st.rerun()

    with t_insumos:
        st.markdown("#### 🧪 Insumos Técnicos para Respuesta Contingencial a Brotes")
        df_solo_insumos = df_alertas[df_alertas["Tipo_Item"] == "INSUMO_LAB"] if not df_alertas.empty else pd.DataFrame()
        if not df_solo_insumos.empty:
            st.dataframe(df_solo_insumos[["Fecha_Registro", "Titulo_Nombre", "Descripcion_Cantidad", "Clasificacion_Riesgo"]].rename(columns={"Titulo_Nombre": "Insumo / Kit Técnico", "Descripcion_Cantidad": "Stock Unidades", "Clasificacion_Riesgo": "Código Lote / Ubicación"}), use_container_width=True, hide_index=True)
        else: 
            st.info("Sin registros de stock de reactivos o kits de toma de muestras.")
        
        if st.session_state["rol_conectado"] == "Administrador Total":
            with st.expander("➕ Actualizar Stock de Insumos Críticos"):
                with st.form("form_insumos", clear_on_submit=True):
                    ins_nombre = st.text_input("Nombre Técnico del Reactivo / Insumo:", placeholder="Ej: Medios de Transporte Viral (MTV)")
                    ins_cant = st.text_input("Cantidad Disponible:", placeholder="Ej: 200 Unidades")
                    ins_lote = st.text_input("Lote / Lugar de Almacenamiento:", placeholder="Ej: LOTE-2026X / Nevera Principal LSP")
                    if st.form_submit_button("💾 Guardar Stock Operativo"):
                        nuevo_i = pd.DataFrame([{"Fecha_Registro": datetime.today().strftime("%Y-%m-%d"), "Tipo_Item": "INSUMO_LAB", "Titulo_Nombre": ins_nombre, "Descripcion_Cantidad": ins_cant, "Clasificacion_Riesgo": ins_lote}])
                        guardar_datos(pd.concat([df_alertas, nuevo_i], ignore_index=True), 'Alertas_Inventario')
                        st.session_state["mensaje_exito_temp"] = "🧪 ¡Inventario de brotes actualizado!"
                        st.rerun()

def vista_filtros_dashboard():
    st.subheader("📊 Analítica Gerencial y Filtros de Búsqueda")
    df_busc = cargar_datos('Eventos')
    df_comp_dash = cargar_datos('Compromisos')
    df_h_dash = cargar_datos('Historial_Enlaces')
    
    col_dash1, col_dash2 = st.columns(2)
    with col_dash1:
        st.markdown("#### 📈 Carga Operativa por Municipios (Eventos)")
        if not df_busc.empty: st.bar_chart(df_busc["Municipio"].value_counts())
        else: st.info("No hay datos de eventos.")
        st.markdown("#### 🏢 Distribución por Espacio Físico")
        if not df_busc.empty: st.bar_chart(df_busc["Lugar"].value_counts())
        else: st.info("No hay datos de espacios.")
    with col_dash2:
        st.markdown("#### 📋 Balance Operativo de Compromisos Técnicos")
        if not df_comp_dash.empty:
            df_comp_dash["Estado_Limpio"] = df_comp_dash["Estado"].apply(lambda x: "FINALIZADO" if "CUMPLIDO" in str(x).upper() or "FINALIZADO" in str(x).upper() else "PENDIENTE")
            st.bar_chart(df_comp_dash["Estado_Limpio"].value_counts())
            st.markdown("📊 **Compromisos Totales Asignados por Funcionario**")
            tabla_resumen = df_comp_dash["Responsable"].value_counts().reset_index()
            tabla_resumen.columns = ["Funcionario", "Tareas Asignadas"]
            st.dataframe(tabla_resumen, use_container_width=True, hide_index=True)
        else: 
            st.info("No hay datos de compromisos para computar analíticas.")
            
    st.markdown("---")
    st.markdown("### 📊 Indicadores de Asistencias Técnicas y Capacitaciones Virtuales")
    if not df_h_dash.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("🌐 Enlaces de Asistencia Creados", len(df_h_dash))
        c2.metric("📋 Tipos de Acciones Únicas", len(df_h_dash["Tipo_Evento"].unique()))
        c3.metric("👥 Ponentes Activos VSP", len(df_h_dash["Responsable_Ponente"].unique()))
        st.bar_chart(df_h_dash["Tipo_Evento"].value_counts())
    else:
        st.info("No se registran datos históricos de enlaces estructurados para computar métricas.")

# =======================================================
# NUEVO: PANEL MAESTRO Y DELEGACIÓN DE ROLES (EXCLUSIVO ADMIN)
# =======================================================
def vista_panel_maestro():
    st.subheader("⚙️ Panel Maestro, Depuración y Seguridad")
    
    t_roles, t_listas, t_depurar, t_backups = st.tabs(["👥 Gestión y Creación de Usuarios", "📝 Editor de Listados", "🗑️ Depuración de Actividades", "🗄️ Backups y Seguridad"])
    
    with t_listas:
        st.markdown("#### 📝 Editor de Listados Maestros")
        st.caption("Los cambios guardados aquí se reflejarán instantáneamente en todos los formularios.")
        listas_actuales = cargar_listas()
        
        c_l1, c_l2 = st.columns(2)
        
        resp_str = "\n".join(listas_actuales.get("LISTA_RESPONSABLES", DEFAULT_LISTAS["LISTA_RESPONSABLES"]))
        nuevos_resp_str = c_l1.text_area("Listado de Responsables / Contratistas:", value=resp_str, height=300, help="Escribe un nombre por línea. No borres 'Seleccione...'.")
        
        eve_str = "\n".join(listas_actuales.get("LISTA_TIPOS_EVENTO", DEFAULT_LISTAS["LISTA_TIPOS_EVENTO"]))
        nuevos_eve_str = c_l2.text_area("Tipos de Evento / Actividades:", value=eve_str, height=300, help="Escribe un evento por línea.")
        
        if st.button("💾 Guardar Cambios en Listados Maestros", type="primary"):
            nuevos_resp = [r.strip() for r in nuevos_resp_str.split("\n") if r.strip()]
            nuevos_eve = [e.strip() for e in nuevos_eve_str.split("\n") if e.strip()]
            
            listas_actuales["LISTA_RESPONSABLES"] = nuevos_resp
            listas_actuales["LISTA_TIPOS_EVENTO"] = nuevos_eve
            guardar_listas(listas_actuales)
            st.success("✅ Listas actualizadas correctamente. Los cambios se aplicarán en todo el sistema. Actualizando interfaz...")
            
            # Recargar la página para aplicar los cambios inmediatamente
            st.rerun()

    with t_roles:
        st.markdown("#### 📝 Registrar Nuevo Funcionario y Asignar Rol")
        df_usuarios = cargar_datos('Usuarios')
        
        with st.form("form_crear_usuario", clear_on_submit=True):
            u_login = st.text_input("Nombre de Usuario (Login):", placeholder="Ej: jgarcia")
            u_pass = st.text_input("Contraseña de Acceso:", type="password")
            u_nombre = st.text_input("Nombre Completo del Funcionario:")
            u_rol_sel = st.selectbox("Definir Nivel de Privilegios (Rol):", [
                "Administrador Total", 
                "Epidemiólogo de Campo / Coordinador", 
                "Líder del Programa",
                "Referente SIVIGILA",
                "Referente VBC",
                "Estadísticas Vitales",
                "Sanidad Portuaria",
                "Referente",
                "Apoyo",
                "Consulta / Invitado",
                "Otro (Especificar manualmente)"
            ])
            if u_rol_sel == "Otro (Especificar manualmente)":
                u_rol = st.text_input("Escriba el rol personalizado:")
            else:
                u_rol = u_rol_sel
            # Multi-select para los permisos exactos
            lista_todas_vistas = list(mapeo_vistas.keys()) if 'mapeo_vistas' in globals() else ["🏠 Inicio", "📝 Registrar Actividad", "🧑‍⚕️ Disponibilidad Semanal", "🤝 Compromisos Técnicos", "📨 Enlaces y Solicitudes HC", "📁 Actas e Informes", "🚨 Alertas e Inventario", "📊 Filtros y Dashboard", "👑 Panel Maestro y Roles", "🏘️ Vigilancia Comunitaria (VBC)", "📊 Tableros SIVIGILA", "🗺️ Georreferenciación", "🛡️ Calidad del Dato", "📇 Directorio de Red", "🪦 Sala de Mortalidades"]
            u_permisos = st.multiselect("Permisos de Acceso a Módulos:", lista_todas_vistas, default=["🏠 Inicio", "📝 Registrar Actividad"])
            
            btn_add_user = st.form_submit_button("👥 Crear y Sincronizar Usuario")
            
        if btn_add_user:
            if u_login.strip() == "" or u_pass.strip() == "" or u_nombre.strip() == "":
                st.error("❌ Todos los campos son obligatorios.")
            elif u_login.strip() in df_usuarios["Usuario"].values:
                st.error("❌ El usuario ya existe.")
            else:
                str_permisos = ",".join(u_permisos)
                nuevo_u = pd.DataFrame([{
                    "Usuario": u_login.strip().lower(), 
                    "Contrasena": u_pass.strip(), 
                    "Nombre_Completo": u_nombre.upper().strip(), 
                    "Rol": u_rol,
                    "Permisos": str_permisos
                }])
                guardar_datos(pd.concat([df_usuarios, nuevo_u], ignore_index=True), 'Usuarios')
                st.success(f"🎉 ¡Usuario creado! {u_nombre.upper()} ({u_rol}).")
                st.rerun()
                
        # Editar perfil completo y permisos de usuarios existentes
        with st.expander("✏️ Editar Perfil y Roles de Usuarios Existentes"):
            u_edit = st.selectbox("Seleccione el usuario a editar:", df_usuarios["Usuario"].tolist(), key="sel_u_edit")
            if u_edit:
                datos_u = df_usuarios[df_usuarios["Usuario"] == u_edit].iloc[0]
                
                # Campos de edición
                e_login = st.text_input("Nombre de Usuario (Login):", value=str(datos_u.get("Usuario", "")))
                e_nombre = st.text_input("Nombre Completo:", value=str(datos_u.get("Nombre_Completo", "")))
                e_pass = st.text_input("Nueva Contraseña (dejar igual si no desea cambiar):", value=str(datos_u.get("Contrasena", "")), type="password")
                
                rol_actual = str(datos_u.get("Rol", "Consulta / Invitado"))
                opciones_roles = [
                    "Administrador Total", "Epidemiólogo de Campo / Coordinador", "Líder del Programa",
                    "Referente SIVIGILA", "Referente VBC", "Estadísticas Vitales", "Sanidad Portuaria",
                    "Referente", "Apoyo", "Consulta / Invitado", "Otro (Especificar manualmente)"
                ]
                indice_rol = opciones_roles.index(rol_actual) if rol_actual in opciones_roles else opciones_roles.index("Otro (Especificar manualmente)")
                e_rol_sel = st.selectbox("Rol Principal:", opciones_roles, index=indice_rol)
                
                if e_rol_sel == "Otro (Especificar manualmente)":
                    e_rol = st.text_input("Escriba el rol personalizado:", value=rol_actual if rol_actual not in opciones_roles else "")
                else:
                    e_rol = e_rol_sel
                
                permisos_actuales = [p.strip() for p in str(datos_u.get("Permisos", "🏠 Inicio,📝 Registrar Actividad")).split(",") if p.strip()]
                lista_todas_vistas_f = list(mapeo_vistas.keys()) if 'mapeo_vistas' in globals() else ["🏠 Inicio", "📝 Registrar Actividad", "🧑‍⚕️ Disponibilidad Semanal", "🤝 Compromisos Técnicos", "📨 Enlaces y Solicitudes HC", "📁 Actas e Informes", "🚨 Alertas e Inventario", "📊 Filtros y Dashboard", "🦠 Brotes y ERI", "🛑 Tablero de Problemas", "🏘️ Vigilancia Comunitaria (VBC)", "📊 Tableros SIVIGILA", "🛡️ Calidad del Dato", "📇 Directorio de Red", "🤖 Asistente Redactor VSP", "👑 Panel Maestro y Roles", "🕵️ Auditoría y Logs", "🪦 Sala de Mortalidades"]
                permisos_actuales = [p for p in permisos_actuales if p in lista_todas_vistas_f]
                
                nuevo_permiso = st.multiselect(f"Permisos de Módulos:", lista_todas_vistas_f, default=permisos_actuales, key=f"ms_{u_edit}")
                
                if st.button("💾 Guardar Cambios del Usuario"):
                    idx_u = df_usuarios.index[df_usuarios["Usuario"] == u_edit].tolist()[0]
                    df_usuarios.at[idx_u, "Usuario"] = e_login.lower().strip()
                    df_usuarios.at[idx_u, "Nombre_Completo"] = e_nombre.upper().strip()
                    df_usuarios.at[idx_u, "Contrasena"] = e_pass.strip()
                    df_usuarios.at[idx_u, "Rol"] = e_rol
                    df_usuarios.at[idx_u, "Permisos"] = ",".join(nuevo_permiso)
                    guardar_datos(df_usuarios, 'Usuarios')
                    
                    # Si se edita a sí mismo, refrescar en tiempo real
                    if st.session_state.get("usuario_conectado") == str(datos_u.get("Nombre_Completo", "")):
                        st.session_state["usuario_conectado"] = e_nombre.upper().strip()
                        st.session_state["rol_conectado"] = e_rol
                        st.session_state["permisos_conectado"] = nuevo_permiso
                    
                    st.success("✅ Perfil actualizado exitosamente.")
                    st.rerun()
                    
        st.markdown("---")
        st.markdown("#### 📋 Usuarios Registrados en el Sistema VSP")
        st.dataframe(df_usuarios[["Nombre_Completo", "Usuario", "Rol"]], use_container_width=True, hide_index=True)
        
        # Eliminar usuario del histórico
        if len(df_usuarios) > 1:
            with st.expander("❌ Dar de baja a un Usuario"):
                usuario_borrar = st.selectbox("Seleccione el usuario a eliminar:", df_usuarios[df_usuarios["Usuario"] != "admin"]["Usuario"].tolist())
                if st.button("Eliminar Cuenta Permanentemente"):
                    df_u_actualizado = df_usuarios[df_usuarios["Usuario"] != usuario_borrar]
                    guardar_datos(df_u_actualizado, 'Usuarios')
                    st.toast(f"Cuenta de {usuario_borrar} eliminada.", icon="ℹ️")
                    st.rerun()

    with t_depurar:
        df_admin = cargar_datos('Eventos')
        if not df_admin.empty:
            df_admin['ID_Fila'] = range(len(df_admin))
            df_admin['Detalle'] = df_admin['Fecha'].astype(str) + " - " + df_admin['Responsable'] + " (" + df_admin['Tipo de Evento'] + ")"
            seleccion = st.selectbox("Seleccione registro para depuración permanente:", ["Seleccione..."] + df_admin['Detalle'].tolist())
            if seleccion != "Seleccione..." and st.button("🚨 ELIMINAR REGISTRO PERMANENTEMENTE"):
                idx = df_admin[df_admin['Detalle'] == seleccion]['ID_Fila'].values[0]
                df_final = df_admin.drop(df_admin.index[idx]).drop(columns=['ID_Fila', 'Detalle'])
                guardar_datos(df_final, 'Eventos')
                st.session_state["mensaje_exito_temp"] = "🗑️ Registro de evento eliminado de la base de datos."
                st.session_state["seccion_actual"] = "🏠 Inicio"; st.rerun()
        else:
            st.info("No hay actividades registradas en la base de datos.")

def vista_vbc():
    st.markdown("### 🏘️ Vigilancia Basada en la Comunidad (VBC)")
    df_vbc = cargar_datos('VBC_Rumores')
    t_reg, t_matriz, t_dash = st.tabs(["📝 Registrar Rumor", "📋 Matriz de Seguimiento", "📊 Analítica VBC"])

    with t_reg:
        with st.form("form_vbc", clear_on_submit=True):
            vbc_fecha = st.date_input("Fecha de Reporte", value=datetime.today())
            vbc_mun = st.selectbox("Municipio", LISTA_MUNICIPIOS)
            vbc_vereda = st.text_input("Comunidad / Vereda / Barrio")
            vbc_sindrome = st.selectbox("Tipo de Evento o Síndrome", ["Síndrome Febril (Posible Dengue/Malaria)", "Síndrome Respiratorio", "Enfermedad Diarreica Aguda (EDA)", "Enfermedad Transmitida por Alimentos (ETA)", "Mortalidad Inusual", "Zoonosis / Animales Enfermos", "Otro"])
            vbc_fuente = st.text_input("Fuente de Información (Ej: Líder, Docente, Redes Sociales)")
            vbc_desc = st.text_area("Descripción Detallada del Evento/Rumor")
            vbc_resp = st.selectbox("Responsable de Verificación", LISTA_RESPONSABLES)
            if st.form_submit_button("🚨 Reportar Alerta a VSP"):
                nuevo_rumor = pd.DataFrame([{
                    "Fecha_Reporte": vbc_fecha.strftime("%Y-%m-%d"), "Municipio": vbc_mun,
                    "Comunidad_Vereda": vbc_vereda, "Tipo_Sindrome": vbc_sindrome,
                    "Fuente_Reporte": vbc_fuente, "Descripcion_Evento": vbc_desc,
                    "Estado_Verificacion": "🔴 Pendiente de Verificación", "Responsable_Verificacion": vbc_resp
                }])
                guardar_datos(pd.concat([df_vbc, nuevo_rumor], ignore_index=True), 'VBC_Rumores')
                st.session_state["mensaje_exito_temp"] = "📢 Alerta comunitaria registrada exitosamente."
                st.rerun()
    with t_matriz:
        if not df_vbc.empty:
            st.dataframe(df_vbc, use_container_width=True, hide_index=True)
            if st.session_state["rol_conectado"] != "Consulta / Invitado":
                st.markdown("#### 🔄 Actualizar Estado de Alerta")
                opciones = [f"{idx} - {row['Municipio']}: {row['Tipo_Sindrome']} ({row['Fecha_Reporte']})" for idx, row in df_vbc.iterrows()]
                sel_rumor = st.selectbox("Seleccione el rumor a verificar:", opciones)
                if sel_rumor:
                    idx_r = int(sel_rumor.split(" - ")[0])
                    nuevo_est = st.selectbox("Estado de la Investigación:", ["🔴 Pendiente de Verificación", "🟡 Descartado / Falsa Alarma", "🟢 Confirmado - Brote Activo", "🟢 Confirmado - Caso Aislado"])
                    if st.button("💾 Actualizar Estado"):
                        df_vbc.at[idx_r, "Estado_Verificacion"] = nuevo_est
                        guardar_datos(df_vbc, 'VBC_Rumores')
                        st.success("Estado actualizado.")
                        st.rerun()
        else:
            st.info("No hay rumores comunitarios registrados.")

    with t_dash:
        if not df_vbc.empty:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("#### Rumores por Municipio")
                st.bar_chart(df_vbc["Municipio"].value_counts())
            with col_g2:
                st.markdown("#### Estado de Verificación")
                st.bar_chart(df_vbc["Estado_Verificacion"].value_counts())
        else:
            st.info("Sin datos para analizar.")

SUCRE_COORDENADAS = {
    "SINCELEJO": {"lat": 9.3047, "lon": -75.3978},
    "COROZAL": {"lat": 9.3142, "lon": -75.2952},
    "SANTIAGO DE TOLU": {"lat": 9.5256, "lon": -75.5816},
    "TOLU": {"lat": 9.5256, "lon": -75.5816},
    "SAN ONOFRE": {"lat": 9.7358, "lon": -75.5269},
    "COVENAS": {"lat": 9.4000, "lon": -75.6833},
    "TOLUVIEJO": {"lat": 9.4500, "lon": -75.4333},
    "MORROA": {"lat": 9.3400, "lon": -75.3100},
    "LOS PALMITOS": {"lat": 9.3800, "lon": -75.2700},
    "SAMPUES": {"lat": 9.1833, "lon": -75.3833},
    "SAN MARCOS": {"lat": 8.6600, "lon": -75.1300},
    "SUCRE": {"lat": 8.8100, "lon": -74.7200},
    "GUARANDA": {"lat": 8.4600, "lon": -74.5300},
    "MAJAGUAL": {"lat": 8.5400, "lon": -74.6200},
    "SINCE": {"lat": 9.2400, "lon": -75.1500},
    "GALERAS": {"lat": 9.1500, "lon": -75.0400},
    "BETULIA": {"lat": 9.2700, "lon": -75.2400},
    "SAN JUAN DE BETULIA": {"lat": 9.2700, "lon": -75.2400},
    "BUENAVISTA": {"lat": 9.2300, "lon": -74.9800},
    "SAN PEDRO": {"lat": 9.3800, "lon": -75.0500},
    "EL ROBLE": {"lat": 9.1000, "lon": -75.1900},
    "CAIMITO": {"lat": 8.8100, "lon": -75.1300},
    "LA UNION": {"lat": 8.8600, "lon": -75.2800},
    "SAN BENITO ABAD": {"lat": 8.9300, "lon": -75.0300},
    "CHALAN": {"lat": 9.5500, "lon": -75.3200},
    "COLOSO": {"lat": 9.5300, "lon": -75.3600},
    "OVEJAS": {"lat": 9.5300, "lon": -75.2300}
}

class PDFBoletin(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'Boletin Epidemiologico - VSP Sucre', 0, 1, 'C', 1)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf_boletin(df, stats_dict):
    pdf = PDFBoletin()
    pdf.add_page()
    pdf.set_font('Arial', '', 11)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Fecha de Generacion: {datetime.today().strftime('%Y-%m-%d')}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. Resumen General de Casos', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, f"Se procesaron un total de {stats_dict['total_casos']} registros en la base de datos suministrada. De estos, los eventos con mayor incidencia registrada corresponden a las dinamicas epidemiologicas observadas en las semanas analizadas.")
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Analisis de Mora en Notificacion', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, f"La mora promedio departamental calculada es de {stats_dict['mora_promedio']} dias, con un pico maximo de mora registrado de {stats_dict['mora_max']} dias.")
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Hospitales / UPGD Criticas', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, "Las siguientes instituciones presentaron demoras significativas en sus reportes, superando los promedios esperados de captura:")
    for inst in stats_dict['peores_upgd']:
        inst_clean = inst.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 8, f" - {inst_clean}", 0, 1)
        
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '4. Hallazgos de Auditoria (Incongruencias)', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, f"El algoritmo de auditoria inteligente detecto {stats_dict['total_incongruencias']} errores clinicos/logicos en las fechas o generos reportados. Estos deben ser revisados urgentemente en la plataforma SIVIGILA oficial.")

    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        temp_path = tmp.name
    pdf.output(temp_path, "F")
    with open(temp_path, "rb") as f:
        pdf_bytes = f.read()
    os.remove(temp_path)
    return pdf_bytes

def vista_sivigila():
    st.markdown("### 📊 Tableros Epidemiológicos y SIVIGILA Pro")
    st.info("Sube tu archivo de rutina SIVIGILA (.csv o .xlsx). Puedes usar la base cruda o la base decodificada.")
    
    archivo_global = st.file_uploader("📂 Cargar Base de Datos SIVIGILA Central", type=["csv", "xlsx"], key="global_siv")
    
    if archivo_global:
        try:
            with st.spinner("Leyendo base de datos..."):
                if archivo_global.name.endswith(".csv"):
                    df_siv = pd.read_csv(archivo_global, encoding='latin1', sep=';')
                    if len(df_siv.columns) < 5: df_siv = pd.read_csv(archivo_global, encoding='utf-8', sep=',')
                else:
                    df_siv = pd.read_excel(archivo_global)
            
            st.success(f"✅ Archivo cargado correctamente: {len(df_siv)} registros analizados.")
            
            df_siv.columns = df_siv.columns.astype(str).str.strip()
            cols_lower = df_siv.columns.str.lower()
            
            col_sem = [c for c in df_siv.columns if 'seman' in c.lower() or 'sem_' in c.lower()][0] if any('seman' in c.lower() or 'sem_' in c.lower() for c in df_siv.columns) else None
            col_sex = [c for c in df_siv.columns if 'sex' in c.lower()][0] if any('sex' in c.lower() for c in df_siv.columns) else None
            col_ed = [c for c in df_siv.columns if 'edad' in c.lower()][0] if any('edad' in c.lower() for c in df_siv.columns) else None
            
            col_mun = None
            posibles_mun = [c for c in df_siv.columns if 'mun_' in c.lower() or 'municipio' in c.lower()]
            if posibles_mun: col_mun = posibles_mun[0]
            
            col_upgd = None
            if 'nom_upgd' in cols_lower: col_upgd = df_siv.columns[cols_lower == 'nom_upgd'][0]
            elif 'cod_upgd' in cols_lower: col_upgd = df_siv.columns[cols_lower == 'cod_upgd'][0]
            else:
                posibles_upgd = [c for c in df_siv.columns if 'upgd' in c.lower() and c.lower() not in ['ndep_upgd', 'nmun_upgd']]
                if posibles_upgd: col_upgd = posibles_upgd[0]
            
            col_evento = None
            if any('evento' in col for col in cols_lower): col_evento = [c for c in df_siv.columns if 'evento' in c.lower()][0]
            elif 'cod_eve' in cols_lower: col_evento = df_siv.columns[cols_lower == 'cod_eve'][0]


            # --- INICIO KPIs Y MAQUINA DEL TIEMPO ---
            if col_sem:
                try:
                    df_siv[col_sem] = pd.to_numeric(df_siv[col_sem], errors='coerce')
                    semana_min = int(df_siv[col_sem].min(skipna=True))
                    semana_max = int(df_siv[col_sem].max(skipna=True))
                    
                    if semana_min < semana_max:
                        st.markdown("### ⏱️ Máquina del Tiempo Epidemiológica")
                        semana_seleccionada = st.slider("Viajar en el tiempo hasta la Semana Epidemiológica:", min_value=semana_min, max_value=semana_max, value=semana_max)
                    else:
                        semana_seleccionada = semana_max
                        st.info(f"📅 Única semana detectada: {semana_max}")
                        
                    # Filtrar la base global
                    df_siv = df_siv[df_siv[col_sem] <= semana_seleccionada]
                    
                    # Calcular KPIs
                    casos_totales = len(df_siv)
                    casos_semana = len(df_siv[df_siv[col_sem] == semana_seleccionada])
                    casos_semana_ant = len(df_siv[df_siv[col_sem] == semana_seleccionada - 1])
                    variacion = 0
                    if casos_semana_ant > 0:
                        variacion = ((casos_semana - casos_semana_ant) / casos_semana_ant) * 100
                        
                    top_evento = "N/A"
                    if col_evento and len(df_siv) > 0:
                        top_evento = df_siv[col_evento].value_counts().index[0][:20] # Top 20 chars
                        
                    mortalidad = 0
                    col_def_kpi = [col for col in df_siv.columns if "fec_def" in col.lower()]
                    if col_def_kpi:
                        # Contar los que no son nulos ni vacíos ni "NaT"
                        mortalidad = df_siv[col_def_kpi[0]].replace(['', 'NaT', 'nan', 'NaN'], np.nan).notna().sum()
                        
                    st.markdown("---")
                    k1, k2, k3, k4, k5 = st.columns(5)
                    k1.metric("🏥 Casos Acumulados", f"{casos_totales:,}")
                    k2.metric(f"📅 Cas. Sem {semana_seleccionada}", f"{casos_semana:,}")
                    k3.metric("📈 Crecimiento", f"{variacion:+.1f}%", delta=f"{variacion:+.1f}%", delta_color="inverse")
                    k4.metric("🚨 Evento Top", str(top_evento))
                    k5.metric("☠️ Mortalidades", f"{mortalidad:,}")
                    st.markdown("---")
                except Exception as e:
                    st.warning(f"No se pudo cargar el módulo de tiempo: {e}")
            # --- FIN KPIs ---

            t0, t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
                "📊 Dashboard BI Analítico",
                "📈 Tablero Gerencial y Mapas", 
                "🏥 Ranking Clínicas/UPGD", 
                "🕵️‍♂️ Auditoría Médica",
                "🔄 Decodificador SIVIGILA",
                "📄 Generar Boletín PDF",
                "🚨 Alertas de Brotes",
                "🏥 Silencio UPGD",
                "🏢 Auditoría EPS"
            ])
            
            with t0:
                st.markdown("### 📊 Dashboard BI Analítico Integral")
                st.info("Esta sección agrupa gráficamente todas las variables demográficas y clínicas de la base de datos hasta la semana seleccionada en la Máquina del Tiempo.")
                
                c_bi1, c_bi2 = st.columns(2)
                
                if col_evento:
                    df_eve = df_siv[col_evento].value_counts().reset_index().head(10)
                    df_eve.columns = ["Evento", "Casos"]
                    fig_eve = px.bar(df_eve, x="Casos", y="Evento", orientation="h", title="Top 10 Eventos de Notificación", color="Casos", color_continuous_scale="Blues")
                    fig_eve.update_layout(yaxis={'categoryorder':'total ascending'})
                    with c_bi1: st.plotly_chart(fig_eve, use_container_width=True)
                
                if col_mun:
                    df_mun = df_siv[col_mun].value_counts().reset_index().head(10)
                    df_mun.columns = ["Municipio", "Casos"]
                    fig_mun = px.bar(df_mun, x="Municipio", y="Casos", title="Top 10 Municipios", color="Casos", color_continuous_scale="Reds")
                    with c_bi2: st.plotly_chart(fig_mun, use_container_width=True)
                    
                c_bi3, c_bi4, c_bi5 = st.columns(3)
                if col_sex:
                    fig_sex = px.pie(df_siv, names=col_sex, title="Distribución por Sexo", hole=0.4)
                    with c_bi3: st.plotly_chart(fig_sex, use_container_width=True)
                
                # Check for EPS col
                cols_lower_bi = df_siv.columns.str.lower()
                col_eapb_bi = None
                if 'eapb_' in cols_lower_bi: col_eapb_bi = df_siv.columns[cols_lower_bi == 'eapb_'][0]
                elif 'cod_ase_' in cols_lower_bi: col_eapb_bi = df_siv.columns[cols_lower_bi == 'cod_ase_'][0]
                elif 'aseguradora' in cols_lower_bi: col_eapb_bi = df_siv.columns[cols_lower_bi == 'aseguradora'][0]
                
                if col_eapb_bi:
                    df_eps = df_siv[col_eapb_bi].value_counts().reset_index().head(7)
                    df_eps.columns = ["EPS", "Casos"]
                    fig_eps = px.pie(df_eps, names="EPS", values="Casos", title="Carga por EPS (Top 7)")
                    with c_bi4: st.plotly_chart(fig_eps, use_container_width=True)
                    
                if col_ed:
                    try:
                        df_edad = df_siv.copy()
                        df_edad[col_ed] = pd.to_numeric(df_edad[col_ed], errors='coerce')
                        # Limpiar edades irreales
                        df_edad = df_edad[(df_edad[col_ed] >= 0) & (df_edad[col_ed] <= 110)]
                        
                        # Crear rangos de edad epidemiológicos (Ciclo Vital)
                        bins = [-1, 5, 11, 18, 28, 59, 120]
                        labels = ['0 a 5 años (Primera Infancia)', '6 a 11 años (Infancia)', '12 a 18 años (Adolescencia)', '19 a 28 años (Juventud)', '29 a 59 años (Adultez)', '60+ años (Adulto Mayor)']
                        df_edad['Ciclo_Vital'] = pd.cut(df_edad[col_ed], bins=bins, labels=labels)
                        
                        df_rangos = df_edad['Ciclo_Vital'].value_counts().reset_index()
                        df_rangos.columns = ['Rango de Edad', 'Casos']
                        df_rangos = df_rangos.sort_index() # Sort by the categorical order
                        
                        fig_ed = px.bar(df_rangos, x="Casos", y="Rango de Edad", orientation="h", title="Afectación por Ciclo de Vida", color="Casos", color_continuous_scale="Purples")
                        with c_bi5: st.plotly_chart(fig_ed, use_container_width=True)
                    except Exception as e:
                        pass

            
            with t1:
                st.markdown("#### 🗺️ Mapa Epidemiológico (Sucre)")
                if col_mun:
                    df_mapa = df_siv.copy()
                    df_mapa["Mun_Normalizado"] = df_mapa[col_mun].astype(str).str.upper().str.strip()
                    import unicodedata
                    df_mapa["Mun_Normalizado"] = df_mapa["Mun_Normalizado"].apply(
                        lambda x: ''.join(c for c in unicodedata.normalize('NFD', str(x)) if unicodedata.category(c) != 'Mn')
                    )
                    
                    df_mapa["Lat"] = df_mapa["Mun_Normalizado"].map(lambda x: SUCRE_COORDENADAS.get(x, {}).get("lat", None))
                    df_mapa["Lon"] = df_mapa["Mun_Normalizado"].map(lambda x: SUCRE_COORDENADAS.get(x, {}).get("lon", None))
                    
                    df_mapa_val = df_mapa.dropna(subset=["Lat", "Lon"])
                    if not df_mapa_val.empty:
                        conteo_mapa = df_mapa_val.groupby(["Mun_Normalizado", "Lat", "Lon"]).size().reset_index(name="Casos")
                        fig_map = px.scatter_mapbox(
                            conteo_mapa, lat="Lat", lon="Lon", size="Casos", color="Casos",
                            hover_name="Mun_Normalizado", zoom=7, mapbox_style="carto-positron",
                            color_continuous_scale="Reds", size_max=40, title="Concentración de Casos por Municipio"
                        )
                        st.plotly_chart(fig_map, use_container_width=True)
                    else:
                        st.info("No se pudieron emparejar los municipios con el mapa.")
                else:
                    st.info("No se detectó columna de municipio para el mapa territorial.")
                    
                st.markdown("#### 📈 Análisis de Tendencia (Semanas y Acumulado)")
                if col_sem:
                    c_t1, c_t2 = st.columns(2)
                    try:
                        if col_evento:
                            # 1. Grafica por semanas (Area)
                            df_tendencia = df_siv.groupby([col_sem, col_evento]).size().reset_index(name="Casos")
                            top_5 = df_siv[col_evento].value_counts().head(5).index
                            df_tendencia_top = df_tendencia[df_tendencia[col_evento].isin(top_5)]
                            df_tendencia_top = df_tendencia_top.sort_values(by=[col_sem, col_evento])
                            fig_line = px.area(df_tendencia_top, x=col_sem, y="Casos", color=col_evento, title="Evolución Semanal", markers=True)
                            with c_t1: st.plotly_chart(fig_line, use_container_width=True)
                            
                            # 2. Grafica Acumulada
                            df_acum = df_siv.groupby([col_sem]).size().reset_index(name="Casos_Semana").sort_values(by=col_sem)
                            df_acum["Acumulado"] = df_acum["Casos_Semana"].cumsum()
                            fig_acum = px.line(df_acum, x=col_sem, y="Acumulado", title="Crecimiento Acumulado del Año", markers=True)
                            fig_acum.update_traces(line_color="red", line_width=4, fill="tozeroy")
                            with c_t2: st.plotly_chart(fig_acum, use_container_width=True)
                        else:
                            df_tendencia = df_siv.groupby([col_sem]).size().reset_index(name="Casos").sort_values(by=col_sem)
                            fig_line = px.bar(df_tendencia, x=col_sem, y="Casos", title="Casos por Semana", color="Casos", color_continuous_scale="Reds")
                            with c_t1: st.plotly_chart(fig_line, use_container_width=True)
                            
                            df_tendencia["Acumulado"] = df_tendencia["Casos"].cumsum()
                            fig_acum = px.line(df_tendencia, x=col_sem, y="Acumulado", title="Crecimiento Acumulado", markers=True)
                            with c_t2: st.plotly_chart(fig_acum, use_container_width=True)
                    except Exception as e:
                        st.warning(f"No se pudo graficar la curva temporal: {e}")
                
                st.markdown("---")
                c1_a, c1_b = st.columns(2)
                with c1_a:
                    st.markdown("#### 🚨 Canal Endémico (Alarma Temprana)")
                    if col_sem:
                        conteo_sem = df_siv[col_sem].value_counts().sort_index().reset_index()
                        conteo_sem.columns = ["Semana", "Casos"]
                        
                        media_casos = conteo_sem["Casos"].mean()
                        std_casos = conteo_sem["Casos"].std()
                        umbral = media_casos + (1.2 * std_casos) if pd.notnull(std_casos) else media_casos
                        conteo_sem["Umbral de Alerta"] = umbral
                        
                        fig_canal = px.line(conteo_sem, x="Semana", y=["Casos", "Umbral de Alerta"], 
                                          color_discrete_sequence=["#2ecc71", "#e74c3c"],
                                          title="Evolución Semanal vs Límite de Alarma")
                        
                        brotes = conteo_sem[conteo_sem["Casos"] > conteo_sem["Umbral de Alerta"]]
                        if not brotes.empty:
                            fig_canal.add_scatter(x=brotes["Semana"], y=brotes["Casos"], mode="markers", 
                                                marker=dict(color="red", size=10), name="¡BROTE DETECTADO!")
                            st.error(f"⚠️ ¡Alerta! Se detectó comportamiento de brote epidémico en {len(brotes)} semanas.")
                        
                        st.plotly_chart(fig_canal, use_container_width=True)
                    else:
                        st.warning("No se detectó columna 'semana'.")
                
                with c1_b:
                    st.markdown("#### 👥 Pirámide y Demografía")
                    if col_sex and col_ed:
                        fig_sex = px.pie(df_siv, names=col_sex, title="Distribución por Sexo", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                        st.plotly_chart(fig_sex, use_container_width=True)
                    else:
                        st.warning("No se detectaron columnas de sexo/edad.")

            with t2:
                st.markdown("#### 🏥 Semáforo y Ranking de Hospitales/IPS")
                st.info("Evalúa el rendimiento de notificación de cada institución.")
                if col_upgd:
                    if "Dias de notificacion" not in df_siv.columns:
                        col_not = [col for col in df_siv.columns if "fec_not_" in col.lower()]
                        col_con = [col for col in df_siv.columns if "fec_con_" in col.lower()]
                        if col_not and col_con:
                            try:
                                # import numpy as np removed to prevent shadowing
                                df_siv["Dias de notificacion"] = (pd.to_datetime(df_siv[col_not[0]], errors='coerce', dayfirst=True) - pd.to_datetime(df_siv[col_con[0]], errors='coerce', dayfirst=True)).dt.days
                                df_siv.loc[(df_siv["Dias de notificacion"] < 0) | (df_siv["Dias de notificacion"] > 365), "Dias de notificacion"] = np.nan
                            except: pass
                        cols_lower = df_siv.columns.str.lower()
                    if "Dias de notificacion" in df_siv.columns:
                        agrup_upgd = df_siv.groupby(col_upgd).agg(
                            Total_Casos=(col_upgd, 'count'),
                            Mora_Promedio=("Dias de notificacion", 'mean')
                        ).reset_index()
                    else:
                        agrup_upgd = df_siv.groupby(col_upgd).agg(
                            Total_Casos=(col_upgd, 'count')
                        ).reset_index()
                        agrup_upgd["Mora_Promedio"] = "N/A"
                    
                    agrup_upgd = agrup_upgd.sort_values(by="Total_Casos", ascending=False)
                    st.dataframe(agrup_upgd, use_container_width=True)
                    
                    if "Dias de notificacion" in df_siv.columns:
                        st.markdown("##### 🚨 Las 10 IPS más demoradas (Peor Mora Promedio)")
                        peores = agrup_upgd.sort_values(by="Mora_Promedio", ascending=False).head(10)
                        fig_peores = px.bar(peores, x=col_upgd, y="Mora_Promedio", text_auto='.1f', color="Mora_Promedio", color_continuous_scale="Reds")
                        st.plotly_chart(fig_peores, use_container_width=True)
                else:
                    st.warning("La base de datos no tiene una columna identificable de IPS o UPGD.")

            with t3:
                st.markdown("#### 🕵️‍♂️ Escáner de Errores Médicos y Lógicos")
                st.info("Revisando incongruencias graves en fechas, sexos y edades reportadas al SIVIGILA.")
                incongruencias = []
                
                if 'fec_def_' in cols_lower and 'fec_con_' in cols_lower:
                    c_def = df_siv.columns[cols_lower == 'fec_def_'][0]
                    c_con = df_siv.columns[cols_lower == 'fec_con_'][0]
                    df_fechas = df_siv.copy()
                    df_fechas[c_def] = pd.to_datetime(df_fechas[c_def], errors='coerce', dayfirst=True)
                    df_fechas[c_con] = pd.to_datetime(df_fechas[c_con], errors='coerce', dayfirst=True)
                    err_fechas = df_fechas[df_fechas[c_def] < df_fechas[c_con]]
                    if not err_fechas.empty:
                        for idx, row in err_fechas.iterrows():
                            incongruencias.append({"Fila": idx+2, "Tipo de Error": "Fecha de Defunción MENOR a Fecha de Consulta", "Detalle": f"Consulta: {row[c_con]} | Defunción: {row[c_def]}"})

                if col_sex and col_evento:
                    eventos_femeninos = ["MATERNA", "EMBARAZADA", "MAMA", "CUELLO UTERINO", "GESTANTE"]
                    mask_femeninos = df_siv[col_evento].astype(str).str.contains('|'.join(eventos_femeninos), case=False, na=False)
                    mask_hombres = df_siv[col_sex].astype(str).str.upper().isin(["M", "MASCULINO", "1"])
                    err_sexo = df_siv[mask_femeninos & mask_hombres]
                    if not err_sexo.empty:
                        for idx, row in err_sexo.iterrows():
                            incongruencias.append({"Fila": idx+2, "Tipo de Error": "Enfermedad Materna/Femenina en sexo Masculino", "Detalle": f"Evento: {row[col_evento]} | Sexo: M"})
                
                if col_ed:
                    err_edad = df_siv[(pd.to_numeric(df_siv[col_ed], errors='coerce') < 0) | (pd.to_numeric(df_siv[col_ed], errors='coerce') > 115)]
                    if not err_edad.empty:
                        for idx, row in err_edad.iterrows():
                            incongruencias.append({"Fila": idx+2, "Tipo de Error": "Edad fuera de rangos biológicos (Absurda)", "Detalle": f"Edad reportada: {row[col_ed]}"})

                df_incongruencias = pd.DataFrame(incongruencias)
                st.metric("Total Incongruencias Graves Detectadas", len(df_incongruencias))
                if not df_incongruencias.empty:
                    st.error("Se encontraron los siguientes errores. Es necesario oficiar a las UPGD para ajustar en SIVIGILA Nacional.")
                    st.dataframe(df_incongruencias, use_container_width=True)
                    st.download_button("📥 Exportar Errores", df_incongruencias.to_csv(index=False).encode("utf-8-sig"), "Errores.csv", "text/csv")
                    st.session_state["_incongruencias_count"] = len(df_incongruencias)
                else:
                    st.success("¡Excelente! El escáner no encontró ninguna incongruencia grave de fechas o cruces biológicos.")
                    st.session_state["_incongruencias_count"] = 0

            with t4:
                st.markdown("#### 🔄 Decodificador Automático SIVIGILA")
                st.write("Si subiste la base de datos **cruda**, sube el diccionario aquí para decodificarla. Si ya la subiste decodificada, ignora esta pestaña.")
                archivo_dicc = st.file_uploader("Sube el Diccionario (sivigila_codificacion...)", type=["xlsx"], key="dicc_siv")
                if archivo_dicc:
                    if st.button("🚀 Ejecutar Decodificación y Resumen", type="primary", use_container_width=True):
                        with st.spinner("Procesando y cruzando bases de datos..."):
                            try:
                                datos = df_siv.copy()
                                sivigila = pd.read_excel(archivo_dicc, sheet_name=None)
                                if "CIE10" not in sivigila or "EVENTOS" not in sivigila:
                                    st.error("❌ El archivo de Diccionario debe contener las pestañas 'CIE10' y 'EVENTOS'.")
                                else:
                                    lista_cie10 = sivigila["CIE10"]
                                    lista_eventos = sivigila["EVENTOS"]
                                    
                                    if "cbmte_" in datos.columns:
                                        datos["CAUSA BASICA DE MUERTE"] = datos["cbmte_"].map(dict(zip(lista_cie10["codigo_cie10"], lista_cie10["CIE10"])))
                                        cbmte_index = datos.columns.get_loc("cbmte_") + 1
                                        datos.insert(loc=cbmte_index, column="CAUSA BASICA DE MUERTE", value=datos.pop("CAUSA BASICA DE MUERTE"))
                                    
                                    if "cod_eve" in datos.columns:
                                        datos["TIPO DE NOTIFICACION"] = datos["cod_eve"].map(dict(zip(lista_eventos["cod_eve"], lista_eventos["notificacion"])))
                                        datos["DISPONIBILIDAD_CAPTURA_EN_LINEA"] = datos["cod_eve"].map(dict(zip(lista_eventos["cod_eve"], lista_eventos["disponibilidad_captura_en_linea"])))
                                        codeve_index = datos.columns.get_loc("cod_eve") + 1
                                        datos.insert(loc=codeve_index, column="TIPO DE NOTIFICACION", value=datos.pop("TIPO DE NOTIFICACION"))
                                        datos.insert(loc=codeve_index + 1, column="DISPONIBILIDAD_CAPTURA_EN_LINEA", value=datos.pop("DISPONIBILIDAD_CAPTURA_EN_LINEA"))
                                        
                                        if "evento" in lista_eventos.columns:
                                            datos["NOMBRE_EVENTO"] = datos["cod_eve"].map(dict(zip(lista_eventos["cod_eve"], lista_eventos["evento"])))
                                    
                                    if "fec_not" in datos.columns and "fec_con_" in datos.columns:
                                        datos["fecha_consulta"] = datos["fec_con_"]
                                        datos["fec_not_dt"] = pd.to_datetime(datos["fec_not"], dayfirst=True, errors='coerce')
                                        datos["fec_con_dt"] = pd.to_datetime(datos["fecha_consulta"], dayfirst=True, errors='coerce')
                                        datos["Dias de notificacion"] = (datos["fec_not_dt"] - datos["fec_con_dt"]).dt.days
                                        datos["fec_not"] = datos["fec_not_dt"].dt.strftime("%d/%m/%Y")
                                        datos["fecha_consulta"] = datos["fec_con_dt"].dt.strftime("%d/%m/%Y")
                                        datos.drop(columns=["fec_not_dt", "fec_con_dt"], inplace=True)
                                        fecnot_index = datos.columns.get_loc("fec_not") + 1
                                        datos.insert(loc=fecnot_index, column="fecha_consulta", value=datos.pop("fecha_consulta"))
                                        datos.insert(loc=fecnot_index + 1, column="Dias de notificacion", value=datos.pop("Dias de notificacion"))
                                    
                                    output = io.BytesIO()
                                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                        datos.to_excel(writer, index=False, sheet_name='SIVIGILA_Decodificado')
                                    val_excel = output.getvalue()
                                    
                                    st.success("✅ ¡Procesamiento completado con éxito!")
                                    st.download_button("📥 Descargar Reporte Decodificado", data=val_excel, file_name="Reporte_SIVIGILA_Decodificado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
                            except Exception as e:
                                st.error(f"Error decodificando: {str(e)}")

            with t5:
                st.markdown("#### 📄 Generador Automático de Boletín PDF")
                st.info("Presiona el botón para generar un documento PDF gerencial con el resumen de la base de datos actual.")
                
                if st.button("🖨️ Generar y Descargar Boletín PDF", type="primary"):
                    try:
                        mora_prom = df_siv["Dias de notificacion"].mean() if "Dias de notificacion" in df_siv.columns else 0
                        mora_mx = df_siv["Dias de notificacion"].max() if "Dias de notificacion" in df_siv.columns else 0
                        peores = []
                        if "Dias de notificacion" in df_siv.columns and col_upgd:
                            ag_pdf = df_siv.groupby(col_upgd)["Dias de notificacion"].mean().sort_values(ascending=False).head(3)
                            peores = ag_pdf.index.tolist()
                            
                        stats_dict = {
                            "total_casos": len(df_siv),
                            "mora_promedio": f"{mora_prom:.1f}",
                            "mora_max": f"{mora_mx:.0f}",
                            "peores_upgd": peores if peores else ["No se detectó UPGD / Mora"],
                            "total_incongruencias": st.session_state.get("_incongruencias_count", 0)
                        }
                        
                        pdf_bytes = generar_pdf_boletin(df_siv, stats_dict)
                        st.success("✅ Boletín generado con éxito.")
                        st.download_button("📥 Descargar Boletín PDF", data=pdf_bytes, file_name=f"Boletin_SIVIGILA_{datetime.today().strftime('%Y%m%d')}.pdf", mime="application/pdf", type="primary")
                    except Exception as e:
                        st.error(f"Error al generar PDF: {e}")

            with t6:
                st.markdown("#### 🚨 Alerta de Brotes (Inteligencia Epidemiológica)")
                st.info("El sistema evalúa el comportamiento histórico de cada evento por municipio.")
                
                if col_mun and col_sem and col_evento:
                    df_brotes = df_siv.groupby([col_mun, col_evento, col_sem]).size().reset_index(name='Casos')
                    df_brotes = df_brotes.sort_values(by=col_sem)
                    semana_actual = df_siv[col_sem].max()
                    alertas = []
                    for (mun, eve), grupo in df_brotes.groupby([col_mun, col_evento]):
                        historico = grupo[grupo[col_sem] < semana_actual]['Casos']
                        actual = grupo[grupo[col_sem] == semana_actual]['Casos']
                        if not historico.empty and not actual.empty:
                            media_hist = historico.mean()
                            std_hist = historico.std()
                            if pd.isna(std_hist): std_hist = 0
                            casos_actuales = actual.values[0]
                            umbral = media_hist + (1.5 * std_hist)
                            if casos_actuales > umbral and casos_actuales >= 3:
                                alertas.append({
                                    "Municipio": mun,
                                    "Evento": eve,
                                    "Casos Sem Actual": casos_actuales,
                                    "Promedio Histórico": round(media_hist, 1),
                                    "Crecimiento %": f"{round((casos_actuales - media_hist) / (media_hist if media_hist > 0 else 1) * 100, 1)}%"
                                })
                    if alertas:
                        st.error(f"⚠️ ¡Atención! Se han detectado **{len(alertas)}** posibles brotes anómalos en la semana {semana_actual}.")
                        df_al = pd.DataFrame(alertas).sort_values(by="Casos Sem Actual", ascending=False)
                        st.dataframe(df_al, use_container_width=True)
                        st.download_button("📥 Exportar Brotes", df_al.to_csv(index=False).encode("utf-8-sig"), "Brotes.csv", "text/csv")
                    else:
                        st.success(f"✅ Todo en orden. No se detectaron disparos inusuales de casos en la semana {semana_actual}.")
                else:
                    st.warning("Faltan variables clave (municipio, evento, semana) para calcular brotes.")
                    
            with t7:
                st.markdown("#### 🏥 Radar de Silencio Epidemiológico (UPGD)")
                st.info("Ley INS: Ningún hospital o UPGD puede pasar 1 semana completa sin notificar. Alerta ROJA a partir de 1 semana de silencio.")
                col_upgd = None
                if 'ndep_upgd' in cols_lower and 'cod_pre' in cols_lower and 'cod_sub' in cols_lower:
                    df_siv['UPGD_Concat'] = df_siv['ndep_upgd'].astype(str).str.zfill(2) + df_siv['nmun_upgd'].astype(str).str.zfill(3) + df_siv['cod_pre'].astype(str) + df_siv['cod_sub'].astype(str).str.zfill(2)
                    col_upgd = 'UPGD_Concat'
                    cols_lower = df_siv.columns.str.lower()
                elif 'cod_upgd' in cols_lower: col_upgd = df_siv.columns[cols_lower == 'cod_upgd'][0]
                elif 'upgd' in cols_lower: col_upgd = df_siv.columns[cols_lower == 'upgd'][0]
                
                if col_upgd and col_sem:
                    semana_actual = df_siv[col_sem].max()
                    ultimas_semanas = df_siv.groupby(col_upgd)[col_sem].max().reset_index()
                    ultimas_semanas.columns = ['UPGD', 'Última Semana Reportada']
                    ultimas_semanas['Semanas de Silencio'] = semana_actual - ultimas_semanas['Última Semana Reportada']
                    
                    def clasificar_silencio(semanas):
                        if semanas == 0: return "🟢 AL DÍA"
                        elif semanas == 1: return "🔴 ALERTA ROJA CRÍTICA (Silencio de 1 Sem)"
                        elif semanas <= 3: return "🚨 ROJA PROLONGADA (Requiere BAI)"
                        else: return "🔥 ROJA EXTREMA (Auditoría Integral >4 Sem)"
                        
                    ultimas_semanas['Alerta Normativa INS'] = ultimas_semanas['Semanas de Silencio'].apply(clasificar_silencio)
                    silenciosos = ultimas_semanas[ultimas_semanas['Semanas de Silencio'] > 0].sort_values(by='Semanas de Silencio', ascending=False)
                    
                    m_a, m_b = st.columns(2)
                    m_a.metric("UPGDs Al Día (Semana Actual)", len(ultimas_semanas[ultimas_semanas['Semanas de Silencio'] == 0]))
                    m_b.metric("UPGDs en Silencio (Incumplimiento)", len(silenciosos))
                    if not silenciosos.empty:
                        st.dataframe(silenciosos.style.map(lambda x: 'color: red; font-weight: bold;' if 'ROJA' in str(x) or '🔥' in str(x) else '', subset=['Alerta Normativa INS']), use_container_width=True)
                        st.download_button('📥 Exportar Silencios', silenciosos.to_csv(index=False).encode('utf-8-sig'), 'Silencios.csv', 'text/csv')
                    else:
                        st.success("🏆 ¡Excelente trabajo departamental! Todas las UPGD han notificado en la semana actual.")
                else:
                    st.warning("No se encontró la columna de código de UPGD en la base de datos.")

            with t8:
                st.markdown("#### 🏢 Fiscalización y Auditoría EPS (EAPB)")
                st.info("Rendimiento clínico y oportunidad de atención por Aseguradora.")
                cols_lower = df_siv.columns.str.lower()
                col_eapb = None
                if 'eapb_' in cols_lower: col_eapb = df_siv.columns[cols_lower == 'eapb_'][0]
                elif 'cod_ase_' in cols_lower: col_eapb = df_siv.columns[cols_lower == 'cod_ase_'][0]
                elif 'aseguradora' in cols_lower: col_eapb = df_siv.columns[cols_lower == 'aseguradora'][0]
                
                if col_eapb:
                    df_eps = df_siv.copy()
                    col_con = df_eps.columns[cols_lower == "fec_con_"][0] if "fec_con_" in cols_lower else None
                    col_sin = df_eps.columns[cols_lower == "ini_sin_"][0] if "ini_sin_" in cols_lower else None
                    col_def = df_eps.columns[cols_lower == "fec_def_"][0] if "fec_def_" in cols_lower else None
                    
                    if col_con and col_sin:
                        df_eps[col_con] = pd.to_datetime(df_eps[col_con], errors='coerce', dayfirst=True)
                        df_eps[col_sin] = pd.to_datetime(df_eps[col_sin], errors='coerce', dayfirst=True)
                        df_eps['Dias_Retraso_Atencion'] = (df_eps[col_con] - df_eps[col_sin]).dt.days
                        df_eps.loc[(df_eps['Dias_Retraso_Atencion'] < 0) | (df_eps['Dias_Retraso_Atencion'] > 365), 'Dias_Retraso_Atencion'] = np.nan
                    
                    df_eps['Muerte'] = 0
                    if col_def:
                        df_eps.loc[df_eps[col_def].notna() & (df_eps[col_def].astype(str).str.strip() != ""), 'Muerte'] = 1
                        
                    resumen_eps = df_eps.groupby(col_eapb).agg(
                        Casos_Totales=(col_eapb, 'count'),
                        Mortalidades=('Muerte', 'sum'),
                        Promedio_Dias_Retraso=('Dias_Retraso_Atencion', 'mean') if col_con and col_sin else (col_eapb, lambda x: np.nan)
                    ).reset_index()
                    resumen_eps['Tasa Mortalidad (%)'] = round((resumen_eps['Mortalidades'] / resumen_eps['Casos_Totales']) * 100, 2)
                    resumen_eps['Promedio_Dias_Retraso'] = round(resumen_eps['Promedio_Dias_Retraso'], 1)
                    resumen_eps = resumen_eps[resumen_eps['Casos_Totales'] >= 5]
                    
                    e1, e2 = st.columns(2)
                    with e1:
                        st.write("**Peores EPS por Oportunidad de Atención (Días en ir al médico):**")
                        p1 = resumen_eps.sort_values(by='Promedio_Dias_Retraso', ascending=False).head(10)
                        st.dataframe(p1[[col_eapb, 'Promedio_Dias_Retraso', 'Casos_Totales']], use_container_width=True)
                        st.download_button('📥 Exportar EPS Lentas', p1[[col_eapb, 'Promedio_Dias_Retraso', 'Casos_Totales']].to_csv(index=False).encode('utf-8-sig'), 'EPS_Lentas.csv', 'text/csv')
                    with e2:
                        st.write("**Top Mortalidad por EPS (% de fallecidos vs atendidos):**")
                        p2 = resumen_eps.sort_values(by='Tasa Mortalidad (%)', ascending=False).head(10)
                        st.dataframe(p2[[col_eapb, 'Mortalidades', 'Tasa Mortalidad (%)']], use_container_width=True)
                        st.download_button('📥 Exportar Mortalidad EPS', p2[[col_eapb, 'Mortalidades', 'Tasa Mortalidad (%)']].to_csv(index=False).encode('utf-8-sig'), 'EPS_Mortalidad.csv', 'text/csv')
                else:
                    st.warning("No se detectó la columna EAPB (Aseguradora).")
                    


        except Exception as e:
            st.error(f"Error procesando el archivo principal: {e}")


class PDFMortalidad(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(220, 53, 69)  # Rojo oscuro
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, 'Ficha Resumen de Unidad de Analisis - Mortalidad VSP', 0, 1, 'C', 1)
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generado automaticamente - Sistema VSP - Pagina {self.page_no()}', 0, 0, 'C')

def vista_sala_mortalidades():
    st.markdown("<h2 class='main-title'>🪦 Sala de Análisis de Mortalidades</h2>", unsafe_allow_html=True)
    st.info("Módulo especializado para la trazabilidad y control normativo (INS) de muertes de interés en Salud Pública.")
    
    archivo_mort = st.file_uploader("📂 Cargar Base SIVIGILA para analizar Mortalidades", type=["csv", "xlsx"], key="mort_siv")
    if archivo_mort:
        try:
            with st.spinner("Escaneando defunciones..."):
                if archivo_mort.name.endswith(".csv"):
                    df = pd.read_csv(archivo_mort, encoding='latin1', sep=';')
                    if len(df.columns) < 5: df = pd.read_csv(archivo_mort, encoding='utf-8', sep=',')
                else:
                    df = pd.read_excel(archivo_mort)
            
            df.columns = df.columns.astype(str).str.strip()
            cols_lower = df.columns.str.lower()
            
            if "fec_def_" not in cols_lower:
                st.error("❌ La base de datos no contiene la variable 'fec_def_' (Fecha de defunción).")
                return
            
            col_def = df.columns[cols_lower == "fec_def_"][0]
            col_con = df.columns[cols_lower == "fec_con_"][0] if "fec_con_" in cols_lower else None
            
            df_mort = df[df[col_def].notna() & (df[col_def].astype(str).str.strip() != "")].copy()
            
            if df_mort.empty:
                st.success("¡Excelente noticia! No se detectaron defunciones en la base de datos suministrada.")
                return
            
            # Limpieza y parseo de fechas
            df_mort["fec_def_dt"] = pd.to_datetime(df_mort[col_def], errors='coerce', dayfirst=True)
            df_mort = df_mort.dropna(subset=["fec_def_dt"])
            
            hoy = datetime.today()
            df_mort["Dias_Transcurridos"] = (hoy - df_mort["fec_def_dt"]).dt.days
            
            # Algoritmo INS: 35 días para Unidad de Análisis
            def calcular_semaforo(dias):
                if pd.isna(dias): return "⚪ SIN FECHA"
                if dias <= 15: return "🟢 A TIEMPO (0-15 d)"
                elif dias <= 35: return "🟡 EN RIESGO (16-35 d)"
                else: return "🔴 VENCIDO (>35 d)"
            
            df_mort["Semaforo_UA"] = df_mort["Dias_Transcurridos"].apply(calcular_semaforo)
            
            t1, t2, t3 = st.tabs(["📊 Panorama de Mortalidad", "⏰ Cronómetro de Comités (INS)", "📄 Generador de Pre-Actas"])
            
            with t1:
                st.markdown("#### Radiografía de las Defunciones")
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Fallecidos", len(df_mort))
                m2.metric("Vencidos (Sin comité o impunes)", len(df_mort[df_mort["Semaforo_UA"].str.contains("🔴")]))
                m3.metric("Muertes Recientes (Verdes)", len(df_mort[df_mort["Semaforo_UA"].str.contains("🟢")]))
                
                c_a, c_b = st.columns(2)
                col_eve = df.columns[cols_lower == "nombre_evento"][0] if "nombre_evento" in cols_lower else (df.columns[cols_lower == "evento"][0] if "evento" in cols_lower else None)
                if col_eve:
                    with c_a:
                        fig_eve = px.pie(df_mort, names=col_eve, title="Causas de Mortalidad (Eventos)", hole=0.3)
                        st.plotly_chart(fig_eve, use_container_width=True)
                
                col_mun = [c for c in df_mort.columns if 'mun_' in c.lower() or 'municipio' in c.lower()]
                if col_mun:
                    with c_b:
                        conteo_mun = df_mort[col_mun[0]].value_counts().reset_index()
                        conteo_mun.columns = ["Municipio", "Muertes"]
                        fig_mun = px.bar(conteo_mun, x="Municipio", y="Muertes", title="Muertes por Municipio", text="Muertes", color="Muertes", color_continuous_scale="Reds")
                        st.plotly_chart(fig_mun, use_container_width=True)

            with t2:
                st.markdown("#### Control de Tiempos Exactos (INS)")
                st.info("Ley INS: Máximo 35 días calendario para cargue de UACE en el aplicativo.")
                
                cols_mostrar = [col_def, "Dias_Transcurridos", "Semaforo_UA"]
                if col_eve: cols_mostrar.insert(0, col_eve)
                if col_mun: cols_mostrar.insert(0, col_mun[0])
                if "edad_" in cols_lower: cols_mostrar.append(df.columns[cols_lower == "edad_"][0])
                elif "edad" in cols_lower: cols_mostrar.append(df.columns[cols_lower == "edad"][0])
                
                st.dataframe(df_mort[cols_mostrar].sort_values(by="Dias_Transcurridos", ascending=False), use_container_width=True)
            
            with t3:
                st.markdown("#### Generador de Pre-Actas para Comité")
                st.write("Selecciona una de las defunciones de la base de datos para generar un PDF pre-llenado listo para llevar al comité de la Unidad de Análisis.")
                
                opciones = ["Seleccione un fallecido..."]
                for idx, row in df_mort.iterrows():
                    lbl_mun = row[col_mun[0]] if col_mun else "Desc"
                    lbl_eve = row[col_eve] if col_eve else "Evento Desc"
                    lbl_fec = row[col_def]
                    opciones.append(f"Fila {idx+2}: {lbl_mun} - {lbl_eve} - {lbl_fec}")
                
                sel_fallecido = st.selectbox("Seleccionar Fallecido:", opciones)
                if sel_fallecido != "Seleccione un fallecido...":
                    idx_real = int(sel_fallecido.split(":")[0].replace("Fila ", "")) - 2
                    datos_fall = df_mort.loc[idx_real]
                    
                    if st.button("🖨️ Generar PDF de Unidad de Análisis", type="primary"):
                        pdf = PDFMortalidad()
                        pdf.add_page()
                        pdf.set_font('Arial', 'B', 12)
                        
                        pdf.cell(0, 10, "INFORMACION BAsICA DEL FALLECIDO", 0, 1)
                        pdf.set_font('Arial', '', 11)
                        
                        for k, v in datos_fall.items():
                            if k.lower() not in ["fec_def_dt", "dias_transcurridos", "semaforo_ua"] and pd.notna(v):
                                val_str = str(v).encode('latin-1', 'replace').decode('latin-1')
                                key_str = str(k).encode('latin-1', 'replace').decode('latin-1')
                                pdf.cell(0, 8, f"{key_str}: {val_str}", 0, 1)
                        
                        pdf.ln(5)
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, "ESTADO NORMATIVO (Semaforo INS)", 0, 1)
                        pdf.set_font('Arial', '', 11)
                        pdf.cell(0, 8, f"Dias desde defuncion: {datos_fall['Dias_Transcurridos']} dias.", 0, 1)
                        estado_ins_str = str(datos_fall['Semaforo_UA']).encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(0, 8, f"Estado INS: {estado_ins_str}", 0, 1)
                        
                        pdf.ln(10)
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, "CONCLUSIONES DEL COMITE (UACE):", 0, 1)
                        pdf.set_font('Arial', '', 11)
                        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                        pdf.ln(10)
                        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                        pdf.ln(10)
                        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                        
                        import tempfile
                        import os
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            temp_path = tmp.name
                        pdf.output(temp_path, "F")
                        with open(temp_path, "rb") as f:
                            pdf_bytes = f.read()
                        os.remove(temp_path)
                        
                        st.download_button("📥 Descargar Pre-Acta PDF", data=pdf_bytes, file_name=f"UA_Mortalidad_{datetime.today().strftime('%Y%m%d')}.pdf", mime="application/pdf", type="primary")

        except Exception as e:
            st.error(f"Error procesando módulo de mortalidades: {str(e)}")

def vista_calidad_dato():
    st.markdown("### 🛡️ Módulo de Calidad del Dato")
    st.info("Auditoría automática de bases de datos SIVIGILA.")
    archivo = st.file_uploader("Cargar Base SIVIGILA para Auditoría", type=["csv", "xlsx"], key="calidad")
    if archivo:
        try:
            if archivo.name.endswith(".csv"):
                df_siv = pd.read_csv(archivo, encoding='latin1', sep=';')
                if len(df_siv.columns) < 5: df_siv = pd.read_csv(archivo, encoding='utf-8', sep=',')
            else:
                df_siv = pd.read_excel(archivo)
            
            nulos = df_siv.isnull().sum()
            nulos_criticos = nulos[nulos > 0].sort_values(ascending=False)
            st.markdown("#### 🚨 Variables con Datos Faltantes (Inconsistencias)")
            if not nulos_criticos.empty:
                st.dataframe(pd.DataFrame({"Variables": nulos_criticos.index, "Cantidad Nulos": nulos_criticos.values}))
            else:
                st.success("¡Excelente! No hay valores nulos en la base de datos.")
        except Exception as e:
            st.error(f"Error procesando el archivo: {e}")

def vista_directorio():
    st.markdown("### 📞 Directorio de Red Institucional y Notificación Masiva")
    df_dir = cargar_datos('Directorio_Contactos')
    t_lista, t_nuevo = st.tabs(["📋 Directorio de Actores", "➕ Registrar Contacto"])
    
    with t_lista:
        st.markdown("#### 🔗 Directorio Central en la Nube")
        st.link_button("🌐 Abrir Directorio Maestro Completo (Google Sheets)", URL_DIRECTORIO_ENTIDADES, use_container_width=True, type="primary")
        st.caption("Usa este botón para editar el directorio principal hospedado en línea.")
        st.markdown("---")
        
        st.markdown("#### 📋 Base de Datos Auxiliar de Contactos (Local)")
        if not df_dir.empty:
            st.dataframe(df_dir, use_container_width=True, hide_index=True)
            st.markdown("#### 📧 Enviar Notificación Masiva a la Red")
            correos_validos = [c for c in df_dir["Correo"] if "@" in str(c)]
            if correos_validos:
                lista_bcc = ",".join(correos_validos)
                st.markdown(f'<a href="mailto:?bcc={lista_bcc}&subject=ALERTA EPIDEMIOLOGICA VSP SUCRE"><button style="padding:10px; background-color:#eab308; border:none; border-radius:5px; color:black; font-weight:bold;">✉️ Generar Correo a Todos los Actores ({len(correos_validos)} correos)</button></a>', unsafe_allow_html=True)
        else:
            st.info("Directorio vacío.")
            
    with t_nuevo:
        with st.form("form_dir", clear_on_submit=True):
            dir_nombre = st.text_input("Nombre Completo:")
            dir_entidad = st.text_input("Entidad (EPS, IPS, Sec. Salud):")
            dir_mun = st.selectbox("Municipio:", LISTA_MUNICIPIOS)
            dir_correo = st.text_input("Correo Electrónico:")
            dir_tel = st.text_input("Teléfono:")
            dir_rol = st.text_input("Cargo / Rol:")
            if st.form_submit_button("💾 Guardar Contacto"):
                nuevo_c = pd.DataFrame([{"Nombre": dir_nombre, "Entidad": dir_entidad, "Municipio": dir_mun, "Correo": dir_correo, "Telefono": dir_tel, "Rol": dir_rol}])
                guardar_datos(pd.concat([df_dir, nuevo_c], ignore_index=True), 'Directorio_Contactos')
                st.success("Contacto agregado.")
                st.rerun()


def vista_auditoria():
    st.markdown("### 🛡️ Módulo de Auditoría y Logs de Seguridad")
    if st.session_state["rol_conectado"] != "Administrador Total":
        st.error("❌ Acceso Denegado. Solo el Administrador Total puede ver la auditoría del sistema.")
        return
        
    df_logs = cargar_datos('Auditoria_Logs')
    if not df_logs.empty:
        df_logs = df_logs.sort_values(by="Fecha_Hora", ascending=False)
        col1, col2 = st.columns(2)
        with col1:
            busqueda = st.text_input("🔍 Buscar en Logs (Usuario, Acción o Módulo):")
        with col2:
            st.metric("Total de Movimientos Registrados", len(df_logs))
            
        if busqueda:
            mask = df_logs.astype(str).apply(lambda col: col.str.contains(busqueda, case=False, na=False)).any(axis=1)
            df_logs = df_logs[mask]
            
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
        st.caption("Los registros de auditoría son inmutables por diseño para garantizar la transparencia.")
    else:
        st.info("No hay registros de auditoría todavía.")

def vista_brotes_eri():
    st.markdown("### 🚨 Brotes y Equipos de Respuesta Inmediata (ERI)")
    df_brotes = cargar_datos('Brotes_ERI')
    
    t_rep, t_matriz, t_dash = st.tabs(["🔴 Reportar Alerta / Brote", "📋 Matriz y Asignación de ERI", "📊 Analítica de Brotes"])
    
    with t_rep:
        with st.form("form_brote", clear_on_submit=True):
            b_fecha = st.date_input("Fecha de Alerta:", value=datetime.today())
            b_mun = st.selectbox("Municipio Afectado:", LISTA_MUNICIPIOS)
            b_patologia = st.selectbox("Evento / Patología:", ["Dengue", "Malaria", "Enfermedad Diarreica Aguda (EDA)", "Infección Respiratoria Aguda (IRA)", "Intoxicación Masiva", "Otro"])
            b_fuente = st.text_input("Fuente de Notificación (Ej: Hospital Local, Líder, SIVIGILA):")
            b_desc = st.text_area("Descripción de la Situación y Acciones Iniciales:")
            
            if st.form_submit_button("🚨 Declarar Alerta Epidemiológica"):
                if "Seleccione..." in b_mun: st.error("Seleccione un municipio.")
                else:
                    nuevo_brote = pd.DataFrame([{
                        "Fecha_Alerta": b_fecha.strftime("%Y-%m-%d"), "Municipio": b_mun,
                        "Patologia": b_patologia, "Fuente": b_fuente, "Descripcion": b_desc,
                        "Equipo_Asignado": "Pendiente", "Estado": "🔴 ACTIVO", "Ruta_ERI": ""
                    }])
                    guardar_datos(pd.concat([df_brotes, nuevo_brote], ignore_index=True), 'Brotes_ERI')
                    registrar_log(f"Alerta de Brote Declarada: {b_patologia} en {b_mun}", "Brotes y ERI")
                    st.success("Brote registrado con éxito.")
                    st.rerun()

    with t_matriz:
        if not df_brotes.empty:
            st.dataframe(df_brotes[["Fecha_Alerta", "Municipio", "Patologia", "Estado", "Equipo_Asignado"]], use_container_width=True, hide_index=True)
            st.markdown("---")
            st.markdown("#### ⚙️ Gestión de Brote (Asignación y Cierre)")
            opciones_b = [f"{idx} - {row['Patologia']} en {row['Municipio']} ({row['Estado']})" for idx, row in df_brotes.iterrows()]
            sel_brote = st.selectbox("Seleccione el Brote a Gestionar:", opciones_b)
            if sel_brote:
                idx_b = int(sel_brote.split(" - ")[0])
                fila_b = df_brotes.iloc[idx_b]
                
                with st.expander("📝 Desplegar Equipo ERI", expanded=True):
                    eq_asig = st.text_area("Integrantes del Equipo de Respuesta Inmediata (ERI):", value=fila_b["Equipo_Asignado"])
                    if st.button("💾 Asignar Equipo"):
                        df_brotes.at[idx_b, "Equipo_Asignado"] = eq_asig
                        guardar_datos(df_brotes, 'Brotes_ERI')
                        registrar_log(f"Equipo ERI asignado al brote {idx_b}", "Brotes y ERI")
                        st.success("Equipo asignado.")
                        st.rerun()
                        
                with st.expander("✅ Cierre e Informe de Campo (ERI)", expanded=True):
                    n_estado = st.selectbox("Estado del Brote:", ["🔴 ACTIVO", "🟡 CONTROLADO", "🟢 CERRADO"], index=["🔴 ACTIVO", "🟡 CONTROLADO", "🟢 CERRADO"].index(fila_b["Estado"]) if fila_b["Estado"] in ["🔴 ACTIVO", "🟡 CONTROLADO", "🟢 CERRADO"] else 0)
                    doc_eri = st.file_uploader("Adjuntar Informe ERI Definitivo (PDF):", type=["pdf", "docx"])
                    if st.button("💾 Guardar Cierre de Brote"):
                        if doc_eri:
                            os.makedirs(CARPETA_SOPORTES, exist_ok=True)
                            ruta_doc = os.path.join(CARPETA_SOPORTES, f"ERI_{idx_b}_{datetime.today().strftime('%Y%m%d')}.{doc_eri.name.split('.')[-1]}")
                            with open(ruta_doc, "wb") as f: f.write(doc_eri.getbuffer())
                            df_brotes.at[idx_b, "Ruta_ERI"] = ruta_doc
                        df_brotes.at[idx_b, "Estado"] = n_estado
                        guardar_datos(df_brotes, 'Brotes_ERI')
                        registrar_log(f"Brote {idx_b} actualizado a estado {n_estado}", "Brotes y ERI")
                        st.success("Actualizado.")
                        st.rerun()
                
                r_eri = str(fila_b.get("Ruta_ERI", ""))
                if r_eri and r_eri != "nan" and os.path.exists(r_eri):
                    with open(r_eri, "rb") as f:
                        st.download_button("📥 Descargar Informe ERI", data=f.read(), file_name=os.path.basename(r_eri), use_container_width=True)
        else:
            st.info("No hay brotes reportados.")

    with t_dash:
        if not df_brotes.empty:
            c1, c2 = st.columns(2)
            c1.bar_chart(df_brotes["Municipio"].value_counts())
            c2.bar_chart(df_brotes["Patologia"].value_counts())
        else:
            st.info("Sin datos de brotes.")

def vista_tablero_problemas():
    st.markdown("### 🛑 Tablero de Problemas (Issue Tracker VSP)")
    df_prob = cargar_datos('Tablero_Problemas')
    
    t_nuevo, t_tablero = st.tabs(["➕ Reportar Problema", "📋 Tablero Kanban"])
    
    with t_nuevo:
        with st.form("form_prob", clear_on_submit=True):
            p_mun = st.selectbox("Municipio Afectado:", LISTA_MUNICIPIOS)
            p_cat = st.selectbox("Categoría del Problema:", ["Falta de Insumos/Reactivos", "Inconsistencia de Datos (SIVIGILA)", "Problemas de Conectividad/Plataforma", "Falta de Personal en Hospital", "Otro"])
            p_desc = st.text_area("Descripción detallada del bloqueo:")
            p_resp = st.selectbox("Referente VSP Encargado de Resolver:", LISTA_RESPONSABLES)
            
            if st.form_submit_button("📢 Crear Ticket de Problema"):
                if "Seleccione..." in p_mun or not p_desc.strip():
                    st.error("Datos incompletos.")
                else:
                    nuevo_p = pd.DataFrame([{
                        "Fecha_Reporte": datetime.today().strftime("%Y-%m-%d"), "Municipio": p_mun,
                        "Categoría": p_cat, "Descripción": p_desc, "Responsable": p_resp,
                        "Estado": "🔴 ABIERTO", "Respuesta": ""
                    }])
                    guardar_datos(pd.concat([df_prob, nuevo_p], ignore_index=True), 'Tablero_Problemas')
                    registrar_log(f"Problema reportado en {p_mun} ({p_cat})", "Tablero Problemas")
                    st.success("Problema registrado en el tablero.")
                    st.rerun()
                    
    with t_tablero:
        if not df_prob.empty:
            c_abierto, c_proceso, c_resuelto = st.columns(3)
            
            for idx, row in df_prob.iterrows():
                estado = str(row["Estado"])
                tarjeta = f"""
                <div style='background:rgba(30,41,59,0.7); padding:15px; border-radius:10px; border-left: 5px solid {"#ef4444" if "ABIERTO" in estado else "#eab308" if "PROCESO" in estado else "#22c55e"}; margin-bottom:10px;'>
                    <small style='color:gray;'>Ticket #{idx} - {row['Municipio']}</small>
                    <h5 style='margin-top:5px; margin-bottom:5px; color:#e2e8f0;'>{row['Categoria']}</h5>
                    <p style='font-size:0.85em; color:#94a3b8;'>{row['Descripcion']}</p>
                    <small><b>Resuelve:</b> {row['Responsable']}</small>
                </div>
                """
                if "ABIERTO" in estado: c_abierto.markdown(tarjeta, unsafe_allow_html=True)
                elif "PROCESO" in estado: c_proceso.markdown(tarjeta, unsafe_allow_html=True)
                else: c_resuelto.markdown(tarjeta, unsafe_allow_html=True)
                
            st.markdown("---")
            with st.expander("🔄 Actualizar o Resolver Ticket"):
                opciones_p = [f"{idx} - Ticket #{idx} ({row['Municipio']} - {row['Categoria']})" for idx, row in df_prob.iterrows()]
                sel_p = st.selectbox("Seleccione Ticket:", opciones_p)
                if sel_p:
                    idx_p = int(sel_p.split(" - ")[0])
                    n_estado_p = st.selectbox("Nuevo Estado:", ["🔴 ABIERTO", "🟡 EN PROCESO", "🟢 RESUELTO"])
                    n_resp_p = st.text_area("Respuesta o Gestión Realizada:", value=str(df_prob.iloc[idx_p]["Respuesta"]))
                    if st.button("💾 Guardar Gestión"):
                        df_prob.at[idx_p, "Estado"] = n_estado_p
                        df_prob.at[idx_p, "Respuesta"] = n_resp_p
                        guardar_datos(df_prob, 'Tablero_Problemas')
                        registrar_log(f"Ticket #{idx_p} actualizado a {n_estado_p}", "Tablero Problemas")
                        st.success("Ticket actualizado.")
                        st.rerun()
        else:
            st.info("El tablero está limpio. No hay problemas reportados.")

def vista_asistente_ia():
    st.markdown("### 🤖 Asistente Redactor VSP (Generador Inteligente)")
    st.info("Usa este módulo para redactar rápidamente correos institucionales, respuestas a entes de control o comunicados técnicos sin escribir desde cero.")
    
    tipo_texto = st.selectbox("¿Qué deseas que redacte el asistente?", [
        "Seleccione...",
        "Solicitud Formal de Plazo (Ministerio/INS)",
        "Respuesta a Requerimiento de Procuraduría/Contraloría",
        "Convocatoria Urgente a Sala Situacional",
        "Comunicado de Alerta a Hospitales/Clínicas"
    ])
    
    if tipo_texto != "Seleccione...":
        asunto = st.text_input("Asunto/Tema Central:", placeholder="Ej: Brote de Dengue en Sincelejo")
        destinatario = st.text_input("Destinatario (Entidad o Persona):", placeholder="Ej: Instituto Nacional de Salud")
        
        if st.button("✨ Generar Redacción Automática", type="primary"):
            if not asunto or not destinatario:
                st.error("Por favor completa el Asunto y el Destinatario para generar el documento.")
            else:
                fecha_hoy = datetime.today().strftime('%d de %B de %Y')
                
                if "Plazo" in tipo_texto:
                    borrador = f"Sincelejo, {fecha_hoy}\n\nSeñores,\n{destinatario}\n\nAsunto: Solicitud de prórroga para entrega de informe sobre {asunto}.\n\nCordial saludo.\n\nPor medio del presente escrito, y desde la coordinación de Vigilancia en Salud Pública de la Gobernación de Sucre, nos dirigimos a ustedes de la manera más respetuosa para solicitar una extensión del plazo otorgado para la presentación del informe relacionado con {asunto}.\n\nActualmente, nuestro equipo técnico se encuentra consolidando la información de campo enviada por los diferentes municipios, lo cual ha tomado más tiempo del estimado debido a problemas técnicos en el flujo de datos. Nos comprometemos a radicar el informe definitivo en un plazo no mayor a 3 días hábiles.\n\nAgradeciendo de antemano su comprensión y colaboración.\n\nAtentamente,\n\nSubprograma de Vigilancia en Salud Pública\nGobernación de Sucre."
                elif "Requerimiento" in tipo_texto:
                    borrador = f"Sincelejo, {fecha_hoy}\n\nSeñores,\n{destinatario}\n\nAsunto: Respuesta formal a requerimiento sobre {asunto}.\n\nRespetados señores.\n\nEn atención a la solicitud de la referencia, remitida a esta oficina, el equipo de Vigilancia en Salud Pública de la Secretaría de Salud Departamental se permite dar respuesta formal respecto a los hallazgos y seguimientos relacionados con {asunto}.\n\nAdjunto a esta comunicación, encontrarán los soportes técnicos, matrices de Excel y actas de compromisos que evidencian la gestión realizada por nuestro equipo en los municipios afectados. Hemos cumplido con los lineamientos del Instituto Nacional de Salud para mitigar el riesgo descrito.\n\nQuedamos a su entera disposición para cualquier aclaración técnica que requieran sobre los documentos anexos.\n\nCordialmente,\n\nCoordinación de Epidemiología\nGobernación de Sucre."
                elif "Convocatoria" in tipo_texto:
                    borrador = f"**URGENTE - CONVOCATORIA A SALA SITUACIONAL**\n\nFecha: {fecha_hoy}\nDestinatario: {destinatario}\nAsunto: {asunto}\n\nEstimado equipo,\n\nDebido a la evolución epidemiológica reciente referente a {asunto}, se convoca de carácter obligatorio y urgente a una Sala Situacional Extraordinaria.\n\nEl objetivo de la reunión es analizar los datos de la última semana epidemiológica, establecer responsabilidades inmediatas y coordinar el despliegue del Equipo de Respuesta Inmediata (ERI) en la zona de brote.\n\nPor favor, asistir con los informes y bases de datos consolidadas de sus respectivos municipios o áreas de competencia.\n\nSaludos,\nVigilancia en Salud Pública."
                else:
                    borrador = f"COMUNICADO OFICIAL DE ALERTA\n\nDestino: {destinatario}\nAsunto: {asunto}\nFecha de Emisión: {fecha_hoy}\n\nSe informa a toda la red hospitalaria y clínica del departamento que se ha activado una alerta preventiva por {asunto}.\n\nSe requiere fortalecer la captación e intensificar la búsqueda activa institucional y comunitaria para este evento. Recordamos que la notificación en SIVIGILA debe hacerse dentro de las próximas 24 horas frente a cualquier caso probable.\n\nAgradecemos su apoyo en la difusión inmediata de esta circular interna."
                
                st.success("✅ Texto generado exitosamente.")
                st.text_area("Borrador Final (Listo para copiar y pegar):", value=borrador, height=350)

# ==========================================
# FUNCIONES DE MÓDULOS AVANZADOS (INTELIGENCIA EPIDEMIOLÓGICA)
# ==========================================

def vista_mapas_vsp():
    st.markdown("<h2 class='main-title'>🗺️ Módulo de Georreferenciación VSP</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Visualización espacial de brotes y alertas epidemiológicas en Sucre.</p>", unsafe_allow_html=True)
    
    sucre_coords = {
        'SINCELEJO': [9.3047, -75.3978], 'COROZAL': [9.3115, -75.2952], 'SAN MARCOS': [8.5303, -75.1322],
        'SAMPUÉS': [9.1822, -75.3811], 'TOLÚ': [9.5244, -75.5806], 'COVEÑAS': [9.4005, -75.6811],
        'SINCÉ': [9.2458, -75.1481], 'MAJAGUAL': [8.5414, -74.6225], 'GUARANDA': [8.4550, -74.5297],
        'SUCRE': [8.8105, -74.7266], 'MORROA': [9.3364, -75.3056], 'LOS PALMITOS': [9.3814, -75.2678],
        'BUENAVISTA': [9.3086, -74.9669], 'SAN PEDRO': [9.3900, -75.0592], 'BETULIA': [9.2778, -75.2444],
        'GALERAS': [9.1625, -75.0253], 'EL ROBLE': [9.1000, -75.1950], 'CHALÁN': [9.5442, -75.3125],
        'COLOSÓ': [9.4897, -75.3528], 'OVEJAS': [9.5275, -75.2289], 'SAN ONOFRE': [9.7358, -75.5261],
        'TOLUVIEJO': [9.4503, -75.4372], 'CAIMITO': [8.8186, -75.1306], 'LA UNIÓN': [8.8572, -75.2817],
        'SAN BENITO ABAD': [8.9281, -75.0264], 'SAN JUAN DE BETULIA': [9.2778, -75.2444]
    }
    
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    df_brotes = cargar_datos('Brotes_ERI')
    df_alertas = cargar_datos('Tablero_Problemas')
    
    map_data = []
    if len(df_brotes) > 0 or len(df_alertas) > 0:
        brotes_count = df_brotes['Municipio'].value_counts().to_dict() if len(df_brotes) > 0 else {}
        alertas_count = df_alertas['Municipio'].value_counts().to_dict() if len(df_alertas) > 0 else {}
        
        for m, c in sucre_coords.items():
            b_cnt = brotes_count.get(m, 0)
            a_cnt = alertas_count.get(m, 0)
            total = b_cnt + a_cnt
            if total > 0:
                map_data.append({"Municipio": m, "lat": c[0], "lon": c[1], "Eventos": total, "Tipo": "Brote/Alerta"})
        
        if map_data:
            st.success(f"📍 Se encontraron {sum([d['Eventos'] for d in map_data])} eventos activos en {len(map_data)} municipios.")
        else:
            st.info("✅ No hay brotes ni alertas activos en la base de datos.")
    else:
        st.info("✅ No hay registros de brotes o alertas en el sistema.")
        
    if not map_data:
        map_data = [{"Municipio": m, "lat": c[0], "lon": c[1], "Eventos": 0, "Tipo": "Normal"} for m, c in sucre_coords.items()]
        
    df_map = pd.DataFrame(map_data)
    
    try:
        import plotly.express as px
        if df_map['Eventos'].sum() > 0:
            df_map['Tamano'] = df_map['Eventos'] * 15
            fig = px.scatter_mapbox(df_map, lat="lat", lon="lon", hover_name="Municipio", hover_data=["Eventos"],
                                    color="Eventos", color_continuous_scale="Reds", size="Tamano",
                                    zoom=7, height=600, mapbox_style="carto-positron")
        else:
            fig = px.scatter_mapbox(df_map, lat="lat", lon="lon", hover_name="Municipio",
                                    color_discrete_sequence=["#2563eb"], zoom=7, height=600, mapbox_style="carto-positron")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.map(df_map)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
def vista_kanban_casos():
    st.markdown("<h2 class='main-title'>📌 Kanban de Casos Críticos</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Gestión visual de casos de seguimiento estricto.</p>", unsafe_allow_html=True)
    
    df_casos = cargar_datos('Casos_Criticos')
    
    with st.expander("➕ Añadir Nuevo Caso Crítico", expanded=False):
        with st.form("form_nuevo_caso", clear_on_submit=True):
            col1, col2 = st.columns(2)
            c_evento = col1.selectbox("Evento", ["Mortalidad Materna", "Mortalidad Perinatal", "Desnutrición Menores 5 Años", "Morbilidad Materna Extrema", "Otro"])
            c_id = col2.text_input("Identificación / Nombre del Paciente:")
            c_mun = col1.selectbox("Municipio", LISTA_MUNICIPIOS)
            c_fecha = col2.date_input("Fecha de Notificación")
            
            btn_add = st.form_submit_button("Guardar y Añadir al Tablero", type="primary", use_container_width=True)
            
            if btn_add and c_id.strip() != "" and c_mun != "Seleccione...":
                nuevo_c = pd.DataFrame([{
                    "Fecha_Notificacion": c_fecha.strftime("%Y-%m-%d"),
                    "Evento": c_evento,
                    "Identificacion": c_id.upper(),
                    "Municipio": c_mun,
                    "Fase": "1. Notificados",
                    "Dias_Mora": 0
                }])
                df_casos = pd.concat([df_casos, nuevo_c], ignore_index=True)
                guardar_datos(df_casos, 'Casos_Criticos')
                st.session_state["mensaje_exito_temp"] = "✅ Caso crítico añadido al Kanban."
                st.rerun()

    st.markdown("---")
    
    try:
        if not df_casos.empty:
            df_casos["Fecha_Notificacion"] = pd.to_datetime(df_casos["Fecha_Notificacion"])
            df_casos["Dias_Mora"] = (pd.Timestamp.now().normalize() - df_casos["Fecha_Notificacion"]).dt.days
    except Exception:
        pass
        
    filtro_evento = st.selectbox("Filtrar por Evento:", ["Todos"] + list(df_casos['Evento'].unique()) if len(df_casos) > 0 else ["Todos"])
    if filtro_evento != "Todos":
        df_mostrar = df_casos[df_casos['Evento'] == filtro_evento]
    else:
        df_mostrar = df_casos
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    fases = ["1. Notificados", "2. En Recolección HC", "3. Unidad de Análisis Programada", "4. Cerrado / Plan de Mejora"]
    k_cols = st.columns(4)
    
    for i, fase in enumerate(fases):
        with k_cols[i]:
            casos_fase = df_mostrar[df_mostrar['Fase'] == fase] if not df_mostrar.empty else pd.DataFrame()
            st.markdown(f"""
                <div style='background-color: #1e293b; padding: 15px; border-top: 4px solid {"#ef4444" if i==0 else "#eab308" if i==1 else "#3b82f6" if i==2 else "#22c55e"}; border-radius: 8px;'>
                    <h4 style='text-align:center; color:white; font-size: 1.1rem; margin-bottom:0;'>{fase}</h4>
                    <p style='text-align:center; color:#94a3b8; margin:0;'>{len(casos_fase)} Casos</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            for idx, row in casos_fase.iterrows():
                mora_color = "red" if row['Dias_Mora'] > 7 and i < 3 else "green"
                with st.container():
                    st.markdown(f"""
                        <div style='background-color: #0f172a; padding: 12px; border-radius: 6px; border-left: 3px solid {mora_color}; margin-bottom: 5px; font-size: 0.9rem; border: 1px solid #334155;'>
                            <b>{row['Identificacion']}</b><br>
                            <span style='color: #94a3b8;'>{row['Evento']} | {row['Municipio']}</span><br>
                            <small style='color:{mora_color};'>Mora: {row['Dias_Mora']} días</small>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if row['Dias_Mora'] > 7 and i < 3:
                        import urllib.parse
                        asunto = urllib.parse.quote(f"Alerta VSP: Mora en caso crítico ({row['Identificacion']})")
                        cuerpo = urllib.parse.quote(f"Alerta,\n\nEl caso crítico de {row['Evento']} para el paciente {row['Identificacion']} ({row['Municipio']}) lleva {row['Dias_Mora']} días en mora en la fase '{fases[i]}'.\n\nPor favor gestionar la historia clínica o unidad de análisis de inmediato.\n\nAtentamente,\nVigilancia en Salud Pública.")
                        mailto_link = f"mailto:?subject={asunto}&body={cuerpo}"
                        st.markdown(f"<a href='{mailto_link}' target='_blank' style='display:block; text-align:center; padding: 5px; background-color: #7f1d1d; color: white; border-radius: 5px; text-decoration: none; font-size: 0.8rem; margin-bottom: 8px;'>📧 Solicitar Gestión por Correo</a>", unsafe_allow_html=True)
                    
                    if i < 3: 
                        if st.button("Avanzar ➡️", key=f"btn_avanzar_{idx}", help="Mover a la siguiente fase", use_container_width=True):
                            df_casos.at[idx, 'Fase'] = fases[i+1]
                            guardar_datos(df_casos, 'Casos_Criticos')
                            st.rerun()

def vista_silencio_bai():
    st.markdown("<h2 class='main-title'>🏥 Control de Silencio Epidemiológico</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Monitoreo de notificaciones de la red de UPGD/IPS.</p>", unsafe_allow_html=True)
    
    df_ips = cargar_datos('IPS_UPGD')
    
    with st.expander("➕ Añadir Nueva IPS a la Red", expanded=False):
        with st.form("form_nueva_ips", clear_on_submit=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            i_mun = col1.selectbox("Municipio", LISTA_MUNICIPIOS)
            i_nombre = col2.text_input("Nombre de la IPS / Clínica:")
            i_cod = col3.text_input("Código Sede (Opcional):")
            
            btn_add = st.form_submit_button("Guardar IPS", type="primary")
            
            if btn_add and i_nombre.strip() != "" and i_mun != "Seleccione...":
                nueva_ips = pd.DataFrame([{
                    "Municipio": i_mun,
                    "Nombre_IPS": i_nombre.upper(),
                    "Codigo_Sede": i_cod,
                    "Reporto_Ultima_Semana": "Sí",
                    "Fecha_Ultimo_Reporte": datetime.today().strftime("%Y-%m-%d")
                }])
                df_ips = pd.concat([df_ips, nueva_ips], ignore_index=True)
                guardar_datos(df_ips, 'IPS_UPGD')
                st.session_state["mensaje_exito_temp"] = "✅ IPS registrada en la red."
                st.rerun()

    st.markdown("---")
    
    if len(df_ips) == 0:
        st.info("No hay IPS registradas. Por favor, añada clínicas usando el botón de arriba.")
        return
        
    st.markdown("### 🚦 Semáforo de Notificación")
    st.caption("Marque las IPS que NO han reportado esta semana para declararlas en Silencio Epidemiológico.")
    
    for idx, row in df_ips.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{row['Nombre_IPS']}** ({row['Municipio']})")
            
        with col2:
            silencio = row['Reporto_Ultima_Semana'] == "No"
            nuevo_estado = st.toggle("En Silencio", value=silencio, key=f"tgl_{idx}")
            
        with col3:
            if nuevo_estado:
                st.markdown("🔴 **SILENCIO**")
                import urllib.parse
                asunto = urllib.parse.quote(f"URGENTE: Silencio Epidemiológico - {row['Nombre_IPS']}")
                cuerpo = urllib.parse.quote(f"Señores {row['Nombre_IPS']} ({row['Municipio']}),\n\nEl sistema departamental ha detectado que NO han reportado la notificación semanal obligatoria.\n\nPor favor reportar de inmediato en el SIVIGILA o nos veremos obligados a programar una Búsqueda Activa Institucional (BAI) y aplicar las sanciones de ley.\n\nAtentamente,\nVigilancia en Salud Pública.")
                mailto_link = f"mailto:?subject={asunto}&body={cuerpo}"
                st.markdown(f"<a href='{mailto_link}' target='_blank' style='display:inline-block; margin-top:5px; padding: 5px 10px; background-color: #ef4444; color: white; border-radius: 5px; text-decoration: none; font-size: 0.8rem;'>📧 Notificar</a>", unsafe_allow_html=True)
            else:
                st.markdown("🟢 **AL DÍA**")
                
        if (nuevo_estado and row['Reporto_Ultima_Semana'] == "Sí") or (not nuevo_estado and row['Reporto_Ultima_Semana'] == "No"):
            df_ips.at[idx, 'Reporto_Ultima_Semana'] = "No" if nuevo_estado else "Sí"
            df_ips.at[idx, 'Fecha_Ultimo_Reporte'] = datetime.today().strftime("%Y-%m-%d")
            guardar_datos(df_ips, 'IPS_UPGD')
            st.rerun()
            
    st.markdown("---")
    silencios = df_ips[df_ips['Reporto_Ultima_Semana'] == "No"]
    if not silencios.empty:
        st.warning(f"⚠️ Atención: Hay {len(silencios)} IPS en Silencio Epidemiológico. Se debe programar Búsqueda Activa Institucional (BAI).")
        st.dataframe(silencios[['Municipio', 'Nombre_IPS', 'Fecha_Ultimo_Reporte']], use_container_width=True)

def vista_asistente_ins():
    st.markdown("<h2 class='main-title'>🤖 Asistente Inteligente de Protocolos INS</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Buscador semántico offline en documentos técnicos.</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='metric-card' style='padding: 20px;'>", unsafe_allow_html=True)
    
    import PyPDF2
    
    if not os.path.exists("protocolos_ins"):
        os.makedirs("protocolos_ins")
        
    uploaded_file = st.file_uploader("Sube un protocolo del INS en PDF para añadirlo al cerebro:", type="pdf")
    if uploaded_file is not None:
        file_path = os.path.join("protocolos_ins", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Archivo '{uploaded_file.name}' procesado y guardado en la base de conocimiento.")
        
    st.markdown("---")
    
    archivos_locales = os.listdir("protocolos_ins") if os.path.exists("protocolos_ins") else []
    if len(archivos_locales) == 0:
        st.info("No hay protocolos cargados. Sube un PDF arriba para empezar.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
        
    st.markdown(f"**📚 Base de Conocimiento Activa:** {len(archivos_locales)} documentos.")
    
    query = st.text_input("Hazle una pregunta técnica a los protocolos (Ej: '¿Cuáles son los síntomas del dengue grave?'):")
    
    if st.button("Buscar Respuesta 🔎", type="primary"):
        if query.strip() == "":
            st.warning("Escribe una pregunta para buscar.")
        else:
            with st.spinner("Leyendo miles de páginas en milisegundos..."):
                query_words = [w for w in query.lower().split() if len(w) > 3]
                
                resultados = []
                for arch in archivos_locales:
                    path_pdf = os.path.join("protocolos_ins", arch)
                    try:
                        reader = PyPDF2.PdfReader(path_pdf)
                        for i, page in enumerate(reader.pages):
                            texto = page.extract_text()
                            if texto:
                                texto_lower = texto.lower()
                                score = sum(1 for w in query_words if w in texto_lower)
                                if score > 0:
                                    resultados.append({
                                        "archivo": arch,
                                        "pagina": i + 1,
                                        "texto": texto.strip().replace("\n", " "),
                                        "score": score
                                    })
                    except Exception as e:
                        pass
                
                if not resultados:
                    st.error("No encontré información sobre eso en los protocolos actuales. Intenta usar otras palabras.")
                else:
                    resultados.sort(key=lambda x: x['score'], reverse=True)
                    top_resultados = resultados[:3]
                    
                    for r in top_resultados:
                        st.markdown(f"""
                        <div style='background-color: #0f172a; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-bottom: 10px;'>
                            <b>📄 Documento:</b> {r['archivo']} (Pág. {r['pagina']})<br><br>
                            <span style='color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;'>
                                "...{r['texto'][:600]}..."
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                        
    st.markdown("</div>", unsafe_allow_html=True)

def vista_dashboard_sivigila():
    st.markdown("<h2 class='main-title'>📊 Tablero Interactivo SIVIGILA</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Análisis avanzado y cruce de variables a partir de datos crudos (Power BI mode).</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='metric-card' style='padding: 20px;'>", unsafe_allow_html=True)
    
    uploaded_excel = st.file_uploader("📥 Sube el Plano SIVIGILA (.xlsx o .csv):", type=["xlsx", "csv"])
    
    if uploaded_excel is not None:
        try:
            if uploaded_excel.name.endswith('.csv'):
                df_siv = pd.read_csv(uploaded_excel)
            else:
                df_siv = pd.read_excel(uploaded_excel)
                
            st.success(f"✅ ¡Base de datos '{uploaded_excel.name}' cargada con éxito! ({len(df_siv)} registros encontrados)")
            
            cols = df_siv.columns.tolist()
            
            mun_col = next((c for c in cols if 'MUNICIPIO' in c.upper() or 'MPIO' in c.upper()), None)
            evento_col = next((c for c in cols if 'EVENTO' in c.upper() or 'COD_EVE' in c.upper()), None)
            
            # --- SISTEMA DE ALERTAS PREDICTIVAS ---
            try:
                sem_col_pd = next((c for c in cols if 'SEMANA' in c.upper() or 'SEM' in c.upper()), None)
                casos_col_pd = next((c for c in cols if 'CASOS' in c.upper() or 'TOTAL' in c.upper()), None)
                
                if sem_col_pd and mun_col and evento_col and casos_col_pd:
                    df_alertas = df_siv.groupby([mun_col, evento_col, sem_col_pd])[casos_col_pd].sum().reset_index()
                    max_sem = df_alertas[sem_col_pd].max()
                    
                    if pd.notna(max_sem) and max_sem > 1:
                        df_actual = df_alertas[df_alertas[sem_col_pd] == max_sem]
                        df_anterior = df_alertas[df_alertas[sem_col_pd] == max_sem - 1]
                        
                        merged = pd.merge(df_actual, df_anterior, on=[mun_col, evento_col], suffixes=('_actual', '_anterior'))
                        # Incremento > 50% y mas de 5 casos actuales
                        alertas_criticas = merged[(merged[f"{casos_col_pd}_actual"] > 5) & 
                                                (merged[f"{casos_col_pd}_actual"] > merged[f"{casos_col_pd}_anterior"] * 1.5)]
                        
                        if not alertas_criticas.empty:
                            st.error(f"🚨 **¡SISTEMA DE ALERTAS TEMPRANAS ACTIVADO (Semana Epi {max_sem})!** Se detectaron {len(alertas_criticas)} posibles brotes inminentes.")
                            for _, alerta in alertas_criticas.iterrows():
                                ant = int(alerta[f'{casos_col_pd}_anterior'])
                                act = int(alerta[f'{casos_col_pd}_actual'])
                                incr = int(((act / ant) - 1) * 100) if ant > 0 else "N/A"
                                st.warning(f"⚠️ El municipio **{alerta[mun_col]}** presenta un incremento crítico en **{alerta[evento_col]}**: Pasó de {ant} a {act} casos (+{incr}%).")
            except Exception:
                pass
            # ----------------------------------------
            
            st.markdown("### 🎛️ Panel de Filtros Dinámicos")
            col_f1, col_f2 = st.columns(2)
            
            if mun_col and evento_col:
                mun_sel = col_f1.multiselect("Filtrar por Municipio:", df_siv[mun_col].dropna().unique())
                eve_sel = col_f2.multiselect("Filtrar por Evento:", df_siv[evento_col].dropna().unique())
                
                if mun_sel: df_siv = df_siv[df_siv[mun_col].isin(mun_sel)]
                if eve_sel: df_siv = df_siv[df_siv[evento_col].isin(eve_sel)]
                
            st.markdown("---")
            st.markdown("### 📈 Análisis Gráfico")
            
            g_col1, g_col2 = st.columns(2)
            
            with g_col1:
                st.markdown("**Casos por Municipio (Top 10)**")
                if mun_col:
                    casos_mun = df_siv[mun_col].value_counts().head(10)
                    st.bar_chart(casos_mun)
                else:
                    st.warning("No se detectó columna de municipio.")
                    
            with g_col2:
                st.markdown("**Casos por Evento (Top 10)**")
                if evento_col:
                    casos_eve = df_siv[evento_col].value_counts().head(10)
                    st.bar_chart(casos_eve)
                else:
                    st.warning("No se detectó columna de evento.")
                    
            sem_col = next((c for c in cols if 'SEMANA' in c.upper() or 'SEM_EPI' in c.upper()), None)
            if sem_col:
                st.markdown("**Tendencia Temporal (Por Semana Epidemiológica)**")
                tendencia = df_siv[sem_col].value_counts().sort_index()
                st.line_chart(tendencia)
                
            st.markdown("### 📋 Muestra de Datos Procesados")
            st.dataframe(df_siv.head(50), use_container_width=True)
            
        except Exception as e:
            st.error(f"Error procesando el archivo: {e}")
    else:
        st.info("👆 Por favor, sube un archivo plano para generar los tableros. El archivo se procesará localmente de forma segura.")
        
    st.markdown("</div>", unsafe_allow_html=True)

def vista_muestras_laboratorio():
    st.markdown("<h2 class='main-title'>🧪 Trazabilidad de Muestras - LDSP</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Seguimiento de muestras enviadas al Laboratorio Departamental.</p>", unsafe_allow_html=True)
    
    df_muestras = cargar_datos('Muestras_Lab')
    
    with st.expander("➕ Registrar Envío de Nueva Muestra", expanded=False):
        with st.form("form_nueva_muestra", clear_on_submit=True):
            col1, col2 = st.columns(2)
            m_id = col1.text_input("Identificación / Nombre del Paciente:")
            m_mun = col2.selectbox("Municipio de Origen:", LISTA_MUNICIPIOS)
            m_tipo = col1.selectbox("Tipo de Muestra:", ["Suero", "LCR", "Hisopado Nasofaríngeo", "Tejido/Cerebro (Rabia)", "Heces", "Sangre Total", "Otro"])
            m_evento = col2.selectbox("Evento Sospechoso:", ["Dengue", "Zika", "Chikungunya", "Rabia", "IRA / COVID-19", "EDA / Cólera", "Sarampión/Rubeola", "Otro"])
            m_fecha = st.date_input("Fecha de Envío al LDSP:", value=datetime.today())
            
            btn_add = st.form_submit_button("Guardar Registro", type="primary")
            
            if btn_add and m_id.strip() != "" and m_mun != "Seleccione...":
                nueva_m = pd.DataFrame([{
                    "Fecha_Envio": m_fecha.strftime("%Y-%m-%d"),
                    "Paciente_Identificacion": m_id.upper(),
                    "Municipio": m_mun,
                    "Tipo_Muestra": m_tipo,
                    "Evento_Sospechoso": m_evento,
                    "Estado": "Enviada / Pendiente",
                    "Resultado": "N/A",
                    "Dias_Espera": 0
                }])
                df_muestras = pd.concat([df_muestras, nueva_m], ignore_index=True)
                guardar_datos(df_muestras, 'Muestras_Lab')
                st.session_state["mensaje_exito_temp"] = "✅ Muestra registrada exitosamente."
                st.rerun()

    st.markdown("---")
    
    try:
        if not df_muestras.empty:
            df_muestras["Fecha_Envio"] = pd.to_datetime(df_muestras["Fecha_Envio"])
            df_muestras["Dias_Espera"] = (pd.Timestamp.now().normalize() - df_muestras["Fecha_Envio"]).dt.days
    except Exception:
        pass
        
    st.markdown("### 📋 Listado de Muestras Activas")
    
    if df_muestras.empty:
        st.info("No hay muestras registradas actualmente.")
    else:
        for idx, row in df_muestras.iterrows():
            with st.container():
                color_borde = "#3b82f6" if row["Estado"] == "Enviada / Pendiente" else "#10b981" if row["Resultado"] == "Negativo" else "#ef4444"
                
                if pd.api.types.is_datetime64_any_dtype(row['Fecha_Envio']):
                    fecha_str = row['Fecha_Envio'].strftime('%Y-%m-%d')
                else:
                    fecha_str = str(row['Fecha_Envio']).split(' ')[0]
                    
                st.markdown(f"""
                <div style='background-color: #0f172a; padding: 15px; border-radius: 8px; border-left: 5px solid {color_borde}; margin-bottom: 10px;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <h4 style='margin: 0; color: white;'>{row['Paciente_Identificacion']}</h4>
                            <p style='margin: 0; color: #94a3b8; font-size: 0.9rem;'>{row['Tipo_Muestra']} | {row['Evento_Sospechoso']} | {row['Municipio']}</p>
                            <small style='color: #cbd5e1;'>Enviada: {fecha_str} ({row['Dias_Espera']} días de espera)</small>
                        </div>
                        <div style='text-align: right;'>
                            <span style='background-color: #1e293b; padding: 5px 10px; border-radius: 5px; font-weight: bold; color: {color_borde};'>
                                {row['Estado']}
                            </span>
                            <br><br>
                            <b>Resultado:</b> {row['Resultado']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if row["Estado"] == "Enviada / Pendiente":
                    col_b1, col_b2, col_b3 = st.columns([1, 1, 2])
                    if col_b1.button("Positivo 🔴", key=f"pos_{idx}", use_container_width=True):
                        df_muestras.at[idx, 'Estado'] = "Procesada"
                        df_muestras.at[idx, 'Resultado'] = "Positivo"
                        guardar_datos(df_muestras, 'Muestras_Lab')
                        st.rerun()
                    if col_b2.button("Negativo 🟢", key=f"neg_{idx}", use_container_width=True):
                        df_muestras.at[idx, 'Estado'] = "Procesada"
                        df_muestras.at[idx, 'Resultado'] = "Negativo"
                        guardar_datos(df_muestras, 'Muestras_Lab')
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

def vista_gestion_riesgos():
    st.markdown("<h2 class='main-title'>⚠️ Gestión del Riesgo Epidemiológico y Operativo</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Identificación, evaluación y mitigación de amenazas departamentales.</p>", unsafe_allow_html=True)
    
    df_riesgos = cargar_datos('Riesgos_VSP')
    
    t_reg, t_matriz, t_mitigacion = st.tabs(["📝 Identificar Riesgo", "🚥 Matriz de Calor", "🛡️ Mitigación"])
    
    with t_reg:
        with st.form("form_nuevo_riesgo", clear_on_submit=True):
            r_fecha = st.date_input("Fecha de Identificación:", value=datetime.today())
            
            c_r1, c_r2 = st.columns(2)
            r_cat = c_r1.selectbox("Categoría del Riesgo:", ["Biológico / Epidemiológico", "Desastre Natural", "Operativo / Logístico", "Tecnológico / Sistemas", "Social / Orden Público"])
            r_mun = c_r2.selectbox("Municipio Afectado (o Departamental):", ["Nivel Departamental"] + LISTA_MUNICIPIOS)
            
            r_desc = st.text_area("Descripción de la Amenaza o Escenario:")
            
            st.markdown("##### Evaluación del Riesgo (Impacto x Probabilidad)")
            c_e1, c_e2 = st.columns(2)
            r_prob = c_e1.selectbox("Probabilidad de Ocurrencia (1 a 5):", [1, 2, 3, 4, 5], index=2, format_func=lambda x: f"{x} - " + ["Improbable", "Poco Probable", "Posible", "Probable", "Casi Seguro"][x-1])
            r_imp = c_e2.selectbox("Impacto si se Materializa (1 a 5):", [1, 2, 3, 4, 5], index=2, format_func=lambda x: f"{x} - " + ["Leve", "Menor", "Moderado", "Mayor", "Catastrófico"][x-1])
            
            r_resp = st.selectbox("Funcionario Encargado de Vigilancia/Mitigación:", LISTA_RESPONSABLES)
            
            btn_riesgo = st.form_submit_button("Guardar Riesgo Identificado", type="primary")
            
            if btn_riesgo and r_desc.strip() != "":
                puntaje = r_prob * r_imp
                if puntaje <= 4: nivel = "Bajo 🟢"
                elif puntaje <= 9: nivel = "Medio 🟡"
                elif puntaje <= 15: nivel = "Alto 🟠"
                else: nivel = "Extremo 🔴"
                
                nuevo_r = pd.DataFrame([{
                    "Fecha_Registro": r_fecha.strftime("%Y-%m-%d"),
                    "Categoria": r_cat,
                    "Descripcion": r_desc,
                    "Municipio": r_mun,
                    "Probabilidad": r_prob,
                    "Impacto": r_imp,
                    "Nivel_Riesgo": nivel,
                    "Responsable": r_resp,
                    "Estado": "Activo",
                    "Mitigacion": "Sin acciones registradas aún."
                }])
                
                guardar_datos(pd.concat([df_riesgos, nuevo_r], ignore_index=True), 'Riesgos_VSP')
                st.session_state["mensaje_exito_temp"] = f"✅ Riesgo registrado exitosamente. Nivel asignado: {nivel}"
                st.rerun()

    with t_matriz:
        st.markdown("### Mapa de Riesgos Actuales")
        if df_riesgos.empty:
            st.info("No hay riesgos registrados en el sistema.")
        else:
            col_b, col_m, col_a, col_e = st.columns(4)
            bajos = len(df_riesgos[df_riesgos['Nivel_Riesgo'].str.contains("Bajo", na=False)])
            medios = len(df_riesgos[df_riesgos['Nivel_Riesgo'].str.contains("Medio", na=False)])
            altos = len(df_riesgos[df_riesgos['Nivel_Riesgo'].str.contains("Alto", na=False)])
            extremos = len(df_riesgos[df_riesgos['Nivel_Riesgo'].str.contains("Extremo", na=False)])
            
            col_b.metric("🟢 Riesgo Bajo", bajos)
            col_m.metric("🟡 Riesgo Medio", medios)
            col_a.metric("🟠 Riesgo Alto", altos)
            col_e.metric("🔴 Riesgo Extremo", extremos)
            
            st.markdown("#### Detalle de Matriz")
            df_activos = df_riesgos[df_riesgos['Estado'].isin(["Activo", "En Mitigación", "Materializado"])]
            if not df_activos.empty:
                st.dataframe(df_activos[["Nivel_Riesgo", "Categoria", "Descripcion", "Municipio", "Estado", "Responsable"]], use_container_width=True, hide_index=True)
            else:
                st.success("🎉 Todos los riesgos han sido cerrados o controlados.")

    with t_mitigacion:
        st.markdown("### Seguimiento y Control de Riesgos")
        if df_riesgos.empty:
            st.info("No hay riesgos registrados.")
        else:
            activos = df_riesgos[df_riesgos['Estado'] != "Cerrado/Controlado"]
            
            if activos.empty:
                st.success("✅ No hay riesgos pendientes por gestionar.")
            else:
                for idx, row in activos.iterrows():
                    with st.expander(f"{row['Nivel_Riesgo']} | {row['Categoria']} - {row['Municipio']}", expanded=(row['Nivel_Riesgo'].startswith("Extremo"))):
                        st.markdown(f"**Descripción:** {row['Descripcion']}")
                        st.markdown(f"**Responsable:** {row['Responsable']} | **Fecha Registro:** {row['Fecha_Registro']}")
                        
                        with st.form(f"form_mitig_{idx}"):
                            try:
                                index_estado = ["Activo", "En Mitigación", "Materializado", "Cerrado/Controlado"].index(row['Estado'])
                            except ValueError:
                                index_estado = 0
                            nuevo_estado = st.selectbox("Estado del Riesgo:", ["Activo", "En Mitigación", "Materializado", "Cerrado/Controlado"], index=index_estado)
                            nueva_mitigacion = st.text_area("Acciones de Mitigación / Contingencia:", value=str(row['Mitigacion']))
                            
                            if st.form_submit_button("Actualizar Seguimiento", type="primary"):
                                df_riesgos.at[idx, 'Estado'] = nuevo_estado
                                df_riesgos.at[idx, 'Mitigacion'] = nueva_mitigacion
                                guardar_datos(df_riesgos, 'Riesgos_VSP')
                                st.session_state["mensaje_exito_temp"] = "Estado del riesgo actualizado correctamente."
                                st.rerun()

def vista_gestion_cumpleanos():
    if st.session_state.get("rol_conectado") != "Administrador Total":
        st.error("No tienes permisos para ver este módulo.")
        return

    st.markdown("<h2 class='main-title'>🎂 Gestión de Cumpleaños</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Agrega las fechas de nacimiento del equipo. El sistema las inyectará automáticamente en el calendario cada año.</p>", unsafe_allow_html=True)
    
    df_cump = cargar_datos('Cumpleanos')
    
    with st.form("form_nuevo_cumpleanos", clear_on_submit=True):
        c1, c2 = st.columns(2)
        funcionario = c1.selectbox("Funcionario:", LISTA_RESPONSABLES)
        fecha_nac = c2.date_input("Fecha de Nacimiento (El año no importa):")
        
        if st.form_submit_button("Añadir Cumpleaños", type="primary"):
            fecha_str = fecha_nac.strftime("%m-%d")
            if not df_cump.empty and funcionario in df_cump["Funcionario"].values:
                df_cump.loc[df_cump["Funcionario"] == funcionario, "Fecha_Nacimiento"] = fecha_str
            else:
                nuevo = pd.DataFrame([{"Funcionario": funcionario, "Fecha_Nacimiento": fecha_str}])
                df_cump = pd.concat([df_cump, nuevo], ignore_index=True)
            guardar_datos(df_cump, 'Cumpleanos')
            st.session_state["mensaje_exito_temp"] = "Cumpleaños guardado correctamente."
            st.rerun()
            
    st.markdown("### Cumpleaños Registrados")
    if not df_cump.empty:
        for idx, row in df_cump.iterrows():
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{row['Funcionario']}**")
            col2.write(f"Fecha (Mes-Día): {row['Fecha_Nacimiento']}")
            if col3.button("🗑️ Eliminar", key=f"del_cump_{idx}"):
                df_cump = df_cump.drop(idx)
                guardar_datos(df_cump, 'Cumpleanos')
                st.session_state["mensaje_exito_temp"] = "Cumpleaños eliminado."
                st.rerun()
    else:
        st.info("No hay cumpleaños registrados.")

# ==========================================
# 8. ENRUTADOR PRINCIPAL DE LA APLICACIÓN
# ==========================================
mapeo_vistas = {
    "🏠 Inicio": vista_inicio,
    "⚠️ Gestión del Riesgo": vista_gestion_riesgos,
    "📝 Registrar Actividad": vista_registrar_actividad,
    "🛡️ Disponibilidad Semanal": vista_disponibilidad_semanal,
    "📋 Compromisos Técnicos": vista_compromisos_tecnicos,
    "🛠️ Enlaces y Solicitudes HC": vista_enlaces_hc,
    "📄 Actas e Informes": vista_actas_informes,
    "🚨 Alertas e Inventario": vista_alertas_inventario,
    "🔍 Filtros y Dashboard": vista_filtros_dashboard,
    "🚨 Brotes y ERI": vista_brotes_eri,
    "🛑 Tablero de Problemas": vista_tablero_problemas,
    "🏘️ Vigilancia Comunitaria (VBC)": vista_vbc,
    "📈 Tableros SIVIGILA": vista_sivigila,
    "🛡️ Calidad del Dato": vista_calidad_dato,
    "📞 Directorio de Red": vista_directorio,
    "🤖 Asistente Redactor VSP": vista_asistente_ia,
    "🪦 Sala de Mortalidades": vista_sala_mortalidades,
    "🗺️ Georreferenciación": vista_mapas_vsp,
    "📌 Kanban Críticos": vista_kanban_casos,
    "🏥 Silencio Epi": vista_silencio_bai,
    "🤖 Asistente Protocolos": vista_asistente_ins,
    "📊 Tablero Avanzado": vista_dashboard_sivigila,
    "⚙️ Panel Maestro y Roles": vista_panel_maestro,
    "🕵️ Auditoría y Logs": vista_auditoria,
    "🧪 Muestras de Laboratorio": vista_muestras_laboratorio,
    "🎂 Gestionar Cumpleaños": vista_gestion_cumpleanos
}

if st.session_state["seccion_actual"] in mapeo_vistas:
    st.markdown("<div class='ancla-modulo'></div>", unsafe_allow_html=True)
    st.components.v1.html("""<script>
        setTimeout(function() {
            try {
                var elems = window.parent.document.getElementsByClassName('ancla-modulo');
                if (elems && elems.length > 0) {
                    elems[elems.length - 1].scrollIntoView({behavior: 'smooth', block: 'start'});
                } else {
                    window.parent.scrollTo({top: 600, behavior: 'smooth'});
                }
            } catch (e) {}
        }, 200);
    </script>""", height=0)
    mapeo_vistas[st.session_state["seccion_actual"]]()
