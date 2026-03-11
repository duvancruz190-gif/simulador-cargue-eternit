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
        # CSS para centrar y dar estilo sutil al formulario
        st.markdown("""
            <style>
            .main { background-color: #f5f5f5; }
            .login-box {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stButton>button {
                width: 100%;
                background-color: #E30613;
                color: white;
                border-radius: 5px;
                border: none;
            }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            
            # LOGO ORIGINAL: width=220 asegura que no se pixelee al no estirarse
            st.image("logo-eternit-400x150-1.png", width=220)
            
            st.markdown('<p style="color: #1A3A5A; font-weight: bold; margin-top: 10px;">SISTEMA DE PICKING</p>', unsafe_allow_html=True)
            
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            
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
    # 2. ESTILOS CSS PANEL PRINCIPAL
    st.markdown("""
    <style>
        .header-container {
            display: flex;
            justify-content: center;
            padding: 20px;
        }
        .decor-bar {
            background-color: #EEEEEE; 
            border-bottom: 5px solid #E30613; 
            height: 10px; 
            width: 100%;
            margin-bottom: 20px;
        }
        .main-title {
            text-align: center;
            color: #1A3A5A;
            font-family: sans-serif;
        }
        .cabina {
            background: #1A3A5A;
            color: white;
            text-align: center;
            padding: 15px;
            font-weight: bold;
            border-radius: 10px 10px 0 0;
        }
        .celda { background: #27ae60; color: white; text-align: center; padding: 12px; margin: 4px; border-radius: 6px; font-weight: bold; }
        .saldo { background: #f1c40f; color: black; padding: 12px; margin: 4px; border-radius: 6px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    # 3. ENCABEZADO APP
    izq, logo_centro, der = st.columns([1.5, 2, 1.5])
    with logo_centro:
        # Tamaño sutil también para el encabezado interno
        st.image("logo-eternit-400x150-1.png", width=280)

    st.markdown('<div class="decor-bar"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🚛 Smart Picking & Logistic Guide</h1>', unsafe_allow_html=True)

    # 4. SIDEBAR
    with st.sidebar:
        st.header("Datos")
        pedido_raw = st.text_input("Cantidad Teja # 4", value="0")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
    
    # Lógica de carga
    cantidad = int(pedido_raw) if pedido_raw.isdigit() else 0
    PAQUETE, MAX_PAQUETES, MAX_SALDO = 130, 20, 60
    
    if cantidad > (MAX_PAQUETES * PAQUETE + 20 * MAX_SALDO):
        st.error("Excede capacidad")
    else:
        paquetes_ok = min(cantidad // PAQUETE, MAX_PAQUETES)
        sobrante = cantidad - (paquetes_ok * PAQUETE)
        
        saldos_lista = []
        while sobrante > 0:
            valor = min(sobrante, MAX_SALDO)
            saldos_lista.append(valor)
            sobrante -= valor

        s_izq = saldos_lista[0::2]
        s_der = saldos_lista[1::2]
        p_izq = paquetes_ok // 2 + paquetes_ok % 2
        p_der = paquetes_ok // 2

        # 5. VISUAL CAMIÓN
        c_izq, c_der = st.columns([3, 1])
        with c_izq:
            st.markdown('<div class="cabina">CABINA DEL VEHÍCULO</div>', unsafe_allow_html=True)
            for i in range(10):
                r1, r2, r3, r4 = st.columns([1, 1, 1, 1])
                with r1: st.markdown(f'<div class="saldo">{s_izq[i] if i < len(s_izq) else ""}</div>', unsafe_allow_html=True)
                with r2: st.markdown(f'<div class="celda">{"130" if i < p_izq else ""}</div>', unsafe_allow_html=True)
                with r3: st.markdown(f'<div class="celda">{"130" if i < p_der else ""}</div>', unsafe_allow_html=True)
                with r4: st.markdown(f'<div class="saldo">{s_der[i] if i < len(s_der) else ""}</div>', unsafe_allow_html=True)

        with c_der:
            st.subheader("📋 Resumen")
            st.table({"Item": ["Total", "Paquetes", "Saldos"], "Cant": [cantidad, paquetes_ok, len(saldos_lista)]})
