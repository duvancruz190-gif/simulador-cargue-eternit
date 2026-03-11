import streamlit as st

# 1. CONFIGURACIÓN DE SEGURIDAD Y PÁGINA
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

st.set_page_config(page_title="Smart Picking & Logistic Guide", layout="wide")

# URL del logo oficial de Eternit (puedes usar una ruta local si prefieres)
LOGO_URL = "https://eternit.com.co/templates/g5_helium/custom/images/logo-eternit.png"

# Función de Validación de Acceso
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        # Estilos específicos para la pantalla de Login
        st.markdown("""
            <style>
            .login-container {
                background-color: #f8f9fa;
                padding: 40px;
                border-radius: 15px;
                border-top: 10px solid #E30613;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .login-logo {
                width: 250px;
                margin-bottom: 20px;
            }
            .stButton>button {
                width: 100%;
                background-color: #E30613;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1.5, 1])
        
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.image(LOGO_URL, width=280)
            st.markdown('<h3 style="color: #1A3A5A; margin-top:0;">SISTEMA DE PICKING</h3>', unsafe_allow_html=True)
            
            usuario = st.text_input("Correo electrónico", placeholder="ejemplo@correo.com").upper()
            clave = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            if st.button("Ingresar"):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if login():
    # 2. ESTILOS CSS PARA EL CUERPO DE LA APP
    st.markdown("""
    <style>
        .header-container {
            background-color: white;
            padding: 20px 0px;
            display: flex;
            justify-content: center;
        }
        .decor-bar {
            background-color: #EEEEEE; 
            border-bottom: 5px solid #E30613; 
            height: 15px; 
            width: 100%;
            margin-bottom: 20px;
        }
        .main-title {
            text-align: center;
            color: #1A3A5A;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .cabina {
            background: #1A3A5A;
            color: white;
            text-align: center;
            padding: 15px;
            font-weight: bold;
            border-radius: 10px 10px 0 0;
        }
        .celda {
            background: #27ae60;
            color: white;
            text-align: center;
            padding: 12px;
            margin: 4px;
            border-radius: 6px;
            font-weight: bold;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .saldo {
            background: #f1c40f;
            color: black;
            padding: 12px;
            margin: 4px;
            border-radius: 6px;
            text-align: center;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    # 3. ENCABEZADO: LOGO OFICIAL
    izq, logo_centro, der = st.columns([1.5, 2, 1.5])
    with logo_centro:
        # Usamos use_container_width=True pero dentro de una columna controlada para nitidez
        st.image(LOGO_URL, width=350)

    st.markdown('<div class="decor-bar"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🚛 Smart Picking & Logistic Guide</h1>', unsafe_allow_html=True)

    # 4. SIDEBAR Y LÓGICA (Mantenemos tu lógica original)
    with st.sidebar:
        st.header("Entrada de Datos")
        pedido_raw = st.text_input("Ingrese cantidad de Teja de # 4", value="0")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
    
    # --- Cálculos y Distribución (Tu lógica original intacta) ---
    cantidad = int(pedido_raw) if pedido_raw.isdigit() else 0
    PAQUETE = 130
    MAX_PAQUETES = 20
    MAX_SALDO_UNIDAD = 60
    CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (20 * MAX_SALDO_UNIDAD)

    if cantidad > CAPACIDAD_TOTAL:
        st.error(f"⚠️ El pedido excede la capacidad ({CAPACIDAD_TOTAL} unidades).")
    else:
        paquetes_ok = min(cantidad // PAQUETE, MAX_PAQUETES)
        sobrante = cantidad - (paquetes_ok * PAQUETE)
        saldos_lista = []
        while sobrante > 0:
            if sobrante >= MAX_SALDO_UNIDAD:
                saldos_lista.append(MAX_SALDO_UNIDAD)
                sobrante -= MAX_SALDO_UNIDAD
            else:
                saldos_lista.append(sobrante)
                sobrante = 0

        s_izq = [s for i, s in enumerate(saldos_lista) if i % 2 == 0]
        s_der = [s for i, s in enumerate(saldos_lista) if i % 2 != 0]
        p_izq = paquetes_ok // 2 + paquetes_ok % 2
        p_der = paquetes_ok // 2

        # 5. DISTRIBUCIÓN VISUAL DEL CAMIÓN
        col_izq, col_der = st.columns([3, 1])

        with col_izq:
            st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
            for i in range(10):
                r1, r2, r3, r4 = st.columns([1, 1, 1, 1])
                with r1:
                    val = s_izq[i] if i < len(s_izq) else ""
                    st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)
                with r2:
                    val = "130" if i < p_izq else ""
                    st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
                with r3:
                    val = "130" if i < p_der else ""
                    st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
                with r4:
                    val = s_der[i] if i < len(s_der) else ""
                    st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)

        with col_der:
            st.subheader("📋 Resumen")
            st.table({
                "Detalle": ["Total Unidades", "Paquetes (130)", "Saldos"],
                "Valor": [cantidad, paquetes_ok, len(saldos_lista)]
            })
