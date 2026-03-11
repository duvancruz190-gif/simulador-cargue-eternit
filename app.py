import streamlit as st

# 1. CONFIGURACIÓN DE SEGURIDAD (Cambia esto)
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM" 
CLAVE_CORRECTA = "Du854872*"                   

# Configuración de la página
st.set_page_config(page_title="Sistema de Cargue Eternit - Teja #4", layout="wide")

# Función de Validación de Acceso
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        # Diseño de la pantalla de Login
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
                <div style="background-color: #E0E0E0; padding: 30px; border-radius: 15px; border-top: 8px solid #E30613; text-align: center;">
                    <h1 style="color: #E30613; margin-bottom: 0;">ETERNIT</h1>
                    <p style="color: #1A3A5A; font-weight: bold;">SISTEMA DE PICKING</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Inicie sesión para continuar")
            usuario = st.text_input("Correo electrónico")
            clave = st.text_input("Contraseña", type="password")
            
            if st.button("Ingresar"):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos")
        return False
    return True

# Si el usuario se autentica, mostramos el resto de la página
if login():
    
    # BOTÓN DE CERRAR SESIÓN (Opcional, en la barra lateral)
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # -----------------------
    # ESTILOS CSS (Logos y Camión)
    # -----------------------
    st.markdown("""
    <style>
        .custom-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 25px 50px;
            background-color: #E0E0E0;
            border-bottom: 8px solid #E30613;
            border-radius: 12px;
            margin-bottom: 30px;
        }
        .brand-eternit {
            color: #E30613;
            font-size: 45px;
            font-weight: 900;
            font-family: 'Arial Black', sans-serif;
        }
        .brand-elementia {
            color: #1A3A5A;
            font-size: 45px;
            font-weight: 900;
            font-family: 'Arial Black', sans-serif;
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

    # -----------------------
    # ENCABEZADO
    # -----------------------
    st.markdown("""
    <div class="custom-header">
        <div class="brand-eternit">ETERNIT</div>
        <div class="brand-elementia">ELEMENTIA</div>
    </div>
    """, unsafe_allow_html=True)

    st.title("🚛 Picking de Producto: Teja de # 4")

    # -----------------------
    # SIDEBAR Y LÓGICA
    # -----------------------
    with st.sidebar:
        st.header("Entrada de Datos")
        pedido_raw = st.text_input("Ingrese cantidad de Teja de # 4", value="0")
        
        cantidad = 0
        try:
            cantidad = int(pedido_raw)
        except:
            st.error("⚠️ Ingrese un número válido")

    # Parámetros
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

    # -----------------------
    # REPRESENTACIÓN VISUAL
    # -----------------------
    col_izq, col_der = st.columns([3, 1])

    with col_izq:
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        for i in range(10):
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            with c1:
                val = s_izq[i] if i < len(s_izq) else ""
                st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)
            with c2:
                val = "130" if i < p_izq else ""
                st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
            with c3:
                val = "130" if i < p_der else ""
                st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
            with c4:
                val = s_der[i] if i < len(s_der) else ""
                st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)

    with col_der:
        st.subheader("📋 Resumen")
        st.table({
            "Detalle": ["Total Unidades", "Paquetes", "Saldos"],
            "Valor": [cantidad, paquetes_ok, len(saldos_lista)]
        })
