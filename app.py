import streamlit as st

# 1. CONFIGURACIÓN DE SEGURIDAD
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

st.set_page_config(page_title="Smart Picking & Logistic Guide", layout="wide")

# Función de Validación de Acceso
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        # CSS para dejar la pantalla limpia (sin cajas blancas ni bordes)
        st.markdown("""
            <style>
            /* Eliminar el fondo gris y espacios de Streamlit */
            .stApp { background-color: white; }
            .login-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin-top: 50px;
            }
            /* Estilo para los inputs */
            .stTextInput > div > div > input {
                background-color: #f0f2f6;
                border-radius: 5px;
            }
            /* Estilo del botón */
            .stButton > button {
                background-color: #E30613;
                color: white;
                border-radius: 5px;
                border: none;
                width: 100%;
                font-weight: bold;
            }
            /* Ocultar el header de Streamlit para limpieza total */
            header {visibility: hidden;}
            </style>
        """, unsafe_allow_html=True)

        # Usamos columnas solo para centrar el contenido
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            # 1. EL LOGO ORIGINAL (Ajustado para que se vea nítido)
            # Nota: Asegúrate que el nombre coincida exactamente con tu archivo
            st.image("logo-eternit-400x150-1.png", width=300)
            
            # 2. SUBTÍTULO SUTIL
            st.markdown('<p style="color: #1A3A5A; font-weight: bold; margin-top: 10px; font-family: sans-serif;">SISTEMA DE PICKING</p>', unsafe_allow_html=True)
            
            # 3. CAMPOS DE TEXTO
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Ingresar"):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos")
            
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if login():
    # 2. ESTILOS CSS PANEL PRINCIPAL (Una vez logueado)
    st.markdown("""
    <style>
        .decor-bar {
            border-bottom: 5px solid #E30613; 
            width: 100%;
            margin-bottom: 20px;
        }
        .main-title {
            text-align: center;
            color: #1A3A5A;
            font-family: sans-serif;
            font-weight: bold;
        }
        .cabina {
            background: #1A3A5A;
            color: white;
            text-align: center;
            padding: 15px;
            font-weight: bold;
            border-radius: 8px 8px 0 0;
        }
        .celda { background: #27ae60; color: white; text-align: center; padding: 12px; margin: 4px; border-radius: 5px; font-weight: bold; }
        .saldo { background: #f1c40f; color: black; padding: 12px; margin: 4px; border-radius: 5px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    # HEADER INTERNO
    izq, logo_centro, der = st.columns([1.5, 2, 1.5])
    with logo_centro:
        st.image("logo-eternit-400x150-1.png", width=250)

    st.markdown('<div class="decor-bar"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🚛 Smart Picking & Logistic Guide</h1>', unsafe_allow_html=True)

    # SIDEBAR
    with st.sidebar:
        st.header("Control")
        pedido_raw = st.text_input("Cantidad Teja # 4", value="0")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
    
    # Lógica de carga (Tu código original)
    cantidad = int(pedido_raw) if pedido_raw.isdigit() else 0
    PA
