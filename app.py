import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

st.set_page_config(page_title="Eternit | Simulador", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- ESTILOS DE ÚLTIMA GENERACIÓN ---
st.markdown("""
    <style>
        /* Importar fuente moderna */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        
        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
        }

        /* Eliminar elementos innecesarios de Streamlit */
        [data-testid="stHeaderActionElements"], .stMarkdown h1 a, .stMarkdown h2 a { display: none; }

        /* Contenedor principal de Login */
        .login-card {
            max-width: 400px;
            margin: 0 auto;
            padding: 40px;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            text-align: center;
        }

        /* Logo sutil y centrado */
        .logo-img {
            width: 180px; /* Tamaño más pequeño y elegante */
            margin-bottom: 20px;
        }

        /* Título refinado */
        .main-title {
            color: #1A3A5A;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 35px;
        }

        /* Personalización de inputs */
        .stTextInput input {
            border-radius: 10px !important;
            border: 1px solid #f0f2f6 !important;
            padding: 12px !important;
        }

        /* Botón minimalista */
        div.stButton > button:first-child {
            background-color: #E30613;
            color: white;
            border: none;
            font-weight: 600;
            padding: 14px;
            border-radius: 12px;
            width: 100%;
            transition: all 0.3s ease;
            margin-top: 15px;
        }
        div.stButton > button:hover {
            background-color: #b3050f;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(227, 6, 19, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.autenticado:
    # Centrado vertical sutil con columnas
    _, col_central, _ = st.columns([1, 1.2, 1])

    with col_central:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Envoltorio de la tarjeta
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Logo pequeño (usando el nombre de tu archivo)
        st.image("logo-eternit-400x150-1.png", width=200) #

        # Título con tipografía mejorada
        st.markdown('<p class="main-title">Simulador de Cargue</p>', unsafe_allow_html=True)

        # Campos de entrada
        usuario = st.text_input("Usuario", placeholder="ejemplo@eternit.com.co").upper()
        clave = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Ingresar al Sistema"):
            if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Acceso denegado. Verifique sus datos.")
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- INTERFAZ DE CARGA (App principal) ---
    st.sidebar.image("logo-eternit-400x150-1.png", width=150)
    st.sidebar.title("Configuración")
    
    raw_data = st.sidebar.text_area("Pegue el pedido aquí:", height=250)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    if raw_data:
        # (Aquí iría tu lógica de procesamiento de pedido que ya funciona)
        st.success("Pedido cargado correctamente")
    else:
        st.info("👋 Bienvenido. Por favor use el panel lateral para cargar la información del pedido.")
