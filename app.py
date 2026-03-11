import streamlit as st

# 1. CONFIGURACIÓN DE SEGURIDAD
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

st.set_page_config(page_title="Sistema de Cargue Eternit - Teja #4", layout="wide")

# Función de Validación de Acceso
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
                <div style="background-color: #E0E0E0; padding: 30px; border-radius: 15px; border-top: 8px solid #E30613; text-align: center;">
                    <h1 style="color: #E30613; margin-bottom: 0; font-family: Arial Black;">ETERNIT</h1>
                    <p style="color: #1A3A5A; font-weight: bold;">SISTEMA DE PICKING</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Inicie sesión para continuar")
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            
            if st.button("Ingresar"):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos")
        return False
    return True

if login():
    # Estilos CSS
    st.markdown("""
    <style>
        /* Contenedor del encabezado */
        .header-bg {
            background-color: white;
            padding: 10px 20px;
            margin-bottom: 0px;
        }
        
        /* La barra gris delgada con borde rojo inferior */
        .decor-bar {
            background-color: #EEEEEE; /* Gris claro */
            border-bottom: 6px solid #E30613; /* Borde rojo */
            height: 35px; /* Menos grueso */
            width: 100%;
            border-radius: 8px 8px 0 0;
            margin-bottom: 30px;
        }

        .cabina {
            background: #1A3A5A;
            color: white;
            text-align: center;
            padding: 15px;
            font-weight: bold;
            border-radius: 10px 10px 0 0;
            text-transform: uppercase;
        }
        .celda {
            background: #27ae60;
            color: white;
            text-align: center;
            padding: 12px;
            margin: 4px;
            border-radius: 6px;
            font-weight: bold;
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

    # --- ENCABEZADO CON LOGOS ---
    st.markdown('<div class="header-bg">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.image("logo-eternit-400x150-1.png", width=280)
    with c3:
        st.image("Elementia.png", width=250)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BARRA DECORATIVA GRIS Y ROJA (DEBAJO DE LOGOS) ---
    st.markdown('<div class="decor-bar"></div>', unsafe_allow_html=True)

    st.title("🚛 Picking de Producto: Teja de # 4")

    # Sidebar y Lógica de Carga
    with st.sidebar:
        st.header("Entrada de Datos")
        pedido_raw = st.text_input("Ingrese cantidad de Teja de # 4", value="0")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
    
    cantidad = int(pedido_raw) if pedido_raw.isdigit() else 0
    PAQUETE = 130
    MAX_PAQUETES = 20
    MAX_SALDO_UNIDAD = 60
    CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (20 * MAX_SALDO_UNIDAD)

    if cantidad > CAPACIDAD_TOTAL:
        st.error(f"⚠️ El pedido excede la capacidad ({CAPACIDAD_TOTAL} unidades).")
        st.stop()

    # Cálculos
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

    # Distribución Visual
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
            "Detalle": ["Total Unidades", "Paquetes", "Saldos"],
            "Valor": [cantidad, paquetes_ok, len(saldos_lista)]
        })
