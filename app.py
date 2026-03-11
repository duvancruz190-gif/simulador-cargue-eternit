import streamlit as st

# 1. CONFIGURACIÓN DE SEGURIDAD Y PÁGINA
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

st.set_page_config(page_title="Smart Picking & Logistic Guide", layout="wide")

# URL del logo oficial de alta calidad para evitar pixelado
LOGO_URL = "https://eternit.com.co/templates/g5_helium/custom/images/logo-eternit.png"

# Función de Validación de Acceso
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        # Estilos específicos para la pantalla de Login con diseño limpio
        st.markdown("""
            <style>
            .login-container {
                background-color: #ffffff;
                padding: 40px;
                border-radius: 15px;
                border-top: 10px solid #E30613;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                margin-top: 50px;
            }
            .stButton>button {
                width: 100%;
                background-color: #E30613;
                color: white;
                font-weight: bold;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            .stButton>button:hover {
                background-color: #b3050f;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1.2, 1])
        
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.image(LOGO_URL, width=250)
            st.markdown('<h2 style="color: #1A3A5A; margin-bottom: 25px; font-family: sans-serif;">SISTEMA DE PICKING</h2>', unsafe_allow_html=True)
            
            usuario = st.text_input("Correo electrónico", placeholder="usuario@ejemplo.com").upper()
            clave = st.text_input("Contraseña", type="password", placeholder="••••••••")
            
            if st.button("Ingresar al Sistema"):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Intente de nuevo.")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if login():
    # 2. ESTILOS CSS PARA EL PANEL PRINCIPAL
    st.markdown("""
    <style>
        /* Contenedor del encabezado */
        .header-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px 0;
            background-color: white;
        }
        
        /* Barra decorativa gris con borde inferior rojo */
        .decor-bar {
            background-color: #F2F2F2; 
            border-bottom: 6px solid #E30613; 
            height: 12px; 
            width: 100%;
            margin: 10px 0 25px 0;
            border-radius: 3px;
        }

        .main-title {
            text-align: center;
            color: #1A3A5A;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 800;
            margin-bottom: 5px;
        }

        /* Estilos del Camión */
        .cabina {
            background: #1A3A5A;
            color: white;
            text-align: center;
            padding: 15px;
            font-weight: bold;
            border-radius: 12px 12px 0 0;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }
        .celda {
            background: #27ae60;
            color: white;
            text-align: center;
            padding: 12px;
            margin: 4px;
            border-radius: 8px;
            font-weight: bold;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }
        .saldo {
            background: #f1c40f;
            color: black;
            padding: 12px;
            margin: 4px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    # 3. ENCABEZADO PRINCIPAL CON LOGO
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.image(LOGO_URL, width=320)
    
    st.markdown('<div class="decor-bar"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🚛 Smart Picking & Logistic Guide</h1>', unsafe_allow_html=True)

    # 4. SIDEBAR Y ENTRADA DE DATOS
    with st.sidebar:
        st.header("⚙️ Panel de Control")
        pedido_raw = st.text_input("Cantidad de Teja # 4", value="0")
        st.markdown("---")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
    
    # Lógica de carga
    cantidad = int(pedido_raw) if pedido_raw.isdigit() else 0
    PAQUETE = 130
    MAX_PAQUETES = 20
    MAX_SALDO_UNIDAD = 60
    CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (20 * MAX_SALDO_UNIDAD)

    if cantidad > CAPACIDAD_TOTAL:
        st.error(f"⚠️ Capacidad excedida. Máximo permitido: {CAPACIDAD_TOTAL} unidades.")
    else:
        # Cálculos de distribución (Mantenemos tu lógica original exacta)
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

        # 5. RENDERIZADO DEL CAMIÓN
        col_camion, col_resumen = st.columns([3, 1])

        with col_camion:
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

        with col_resumen:
            st.subheader("📋 Resumen")
            st.table({
                "Concepto": ["Unidades Totales", "Paquetes Completos", "Saldos Sueltos"],
                "Cantidad": [cantidad, paquetes_ok, len(saldos_lista)]
            })
