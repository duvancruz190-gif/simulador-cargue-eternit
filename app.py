import streamlit as st

# 1. CONFIGURACIÓN DE SEGURIDAD Y PÁGINA
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

st.set_page_config(page_title="Smart Picking & Logistic Guide", layout="wide")

# Función de Validación de Acceso
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # CAJA DE LOGIN
            st.markdown(f"""
                <div style="background-color: #E0E0E0; padding: 20px; border-radius: 15px; border-top: 8px solid #E30613; text-align: center; margin-bottom: 20px;">
                </div>
            """, unsafe_allow_html=True)
            
            # --- NUEVO LOGO PARA INICIO DE SESIÓN ---
            try:
                st.image("ETERNIT LOGOS.webp", use_container_width=True)
            except:
                st.error("No se encontró el archivo: ETERNIT LOGOS.webp")
            
            st.markdown("<br>", unsafe_allow_html=True)
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
    # 2. ESTILOS CSS
    st.markdown("""
    <style>
        .header-container {
            background-color: white;
            padding: 10px 0px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .decor-bar {
            background-color: #EEEEEE; 
            border-bottom: 5px solid #E30613; 
            height: 30px; 
            width: 100%;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .main-title {
            text-align: center;
            color: #1A3A5A;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            margin-bottom: 10px;
        }
        .celda {
            background: #27ae60;
            color: white;
            text-align: center;
            padding: 12px;
            margin: 4px;
            border-radius: 6px;
            font-weight: bold;
            min-height: 45px;
        }
        .saldo {
            background: #f1c40f;
            color: black;
            padding: 12px;
            margin: 4px;
            border-radius: 6px;
            text-align: center;
            font-weight: bold;
            min-height: 45px;
        }
        .vacio {
            height: 45px;
            margin: 4px;
        }
    </style>
    """, unsafe_allow_html=True)

    # 3. ENCABEZADO (MANTIENE EL LOGO ORIGINAL SEGÚN TU SOLICITUD)
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    izq, logo_centro, der = st.columns([1.5, 2, 1.5])
    with logo_centro:
        try:
            st.image("logo-eternit-400x150-1.png", use_container_width=False)
        except:
            st.markdown("<h2 style='text-align:center;'>ETERNIT</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="decor-bar"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🚛 Smart Picking & Logistic Guide</h1>', unsafe_allow_html=True)

    # 4. PARÁMETROS Y LÓGICA DE CARGA
    PAQUETE = 130
    MAX_PAQUETES = 20
    MAX_SALDO_UNIDAD = 60
    CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (20 * MAX_SALDO_UNIDAD)

    with st.sidebar:
        st.header("📦 Entrada de Datos")
        cantidad = st.number_input("Cantidad de Teja #4", min_value=0, step=1, value=0)
        
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

    if cantidad > CAPACIDAD_TOTAL:
        st.error(f"⚠️ El pedido excede la capacidad máxima de {CAPACIDAD_TOTAL} unidades.")
        st.stop()

    # Cálculos de distribución
    paquetes_ok = cantidad // PAQUETE
    sobrante = cantidad % PAQUETE
    
    saldos_lista = []
    temp_sobrante = sobrante
    while temp_sobrante > 0:
        carga = min(temp_sobrante, MAX_SALDO_UNIDAD)
        saldos_lista.append(carga)
        temp_sobrante -= carga

    s_izq = saldos_lista[::2]
    s_der = saldos_lista[1::2]
    p_izq = (paquetes_ok + 1) // 2
    p_der = paquetes_ok // 2

    # 5. DISTRIBUCIÓN VISUAL
    col_izq, col_der = st.columns([3, 1])

    with col_izq:
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        for i in range(10):
            r1, r2, r3, r4 = st.columns([1, 1, 1, 1])
            
            with r1:
                val = s_izq[i] if i < len(s_izq) else ""
                estilo = "saldo" if val != "" else "vacio"
                st.markdown(f'<div class="{estilo}">{val}</div>', unsafe_allow_html=True)
            with r2:
                val = PAQUETE if i < p_izq else ""
                estilo = "celda" if val != "" else "vacio"
                st.markdown(f'<div class="{estilo}">{val}</div>', unsafe_allow_html=True)
            with r3:
                val = PAQUETE if i < p_der else ""
                estilo = "celda" if val != "" else "vacio"
                st.markdown(f'<div class="{estilo}">{val}</div>', unsafe_allow_html=True)
            with r4:
                val = s_der[i] if i < len(s_der) else ""
                estilo = "saldo" if val != "" else "vacio"
                st.markdown(f'<div class="{estilo}">{val}</div>', unsafe_allow_html=True)

    with col_der:
        st.subheader("📋 Resumen de Carga")
        st.metric(label="Total Unidades", value=cantidad)
        st.metric(label="Paquetes (130)", value=paquetes_ok)
        st.metric(label="Saldos", value=len(saldos_lista))
