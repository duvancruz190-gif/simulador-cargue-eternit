import streamlit as st
from PIL import Image

# 1. CONFIGURACIÓN DE SEGURIDAD
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
            # Contenedor visual mejorado (caja gris con borde rojo)
            st.markdown(f"""
                <div style="background-color: #E0E0E0; padding: 20px; border-radius: 15px; border-top: 8px solid #E30613; text-align: center;">
                </div>
            """, unsafe_allow_html=True)
            
            # --- CORRECCIÓN DEL LOGO ---
            # Insertamos la imagen justo debajo del borde rojo.
            # Usamos el nombre del archivo de alta resolución de Eternit para que se vea nítido.
            # Puedes ajustar el 'width' para que se vea más grande o pequeño.
            try:
                # Intenta cargar el archivo de alta resolución que tienes
                st.image("logo-eternit-400x150-1.png", width=300, caption="")
            except FileNotFoundError:
                # Si no lo encuentra, usa el texto original como respaldo para no romper la app
                st.error("No se encontró el archivo logo-eternit-400x150-1.png. Usando texto de respaldo.")
                st.markdown('<h1 style="color: #E30613; margin-top: -10px; margin-bottom: 0; font-family: Arial Black;">ETERNIT</h1>', unsafe_allow_html=True)

            # Subtítulo (SISTEMA DE PICKING)
            st.markdown(f"""
                <div style="text-align: center; margin-top: -10px;">
                    <p style="color: #1A3A5A; font-weight: bold; font-family: sans-serif;">SISTEMA DE PICKING</p>
                </div>
            """, unsafe_allow_html=True)
            
            # --- FIN DE LA CORRECCIÓN ---
            
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
    # --- RESTO DEL CÓDIGO (Sin cambios) ---
    # 2. ESTILOS CSS (LOGOS, BARRA Y CAMIÓN)
    st.markdown("""
    <style>
        /* Contenedor blanco para el encabezado */
        .header-container {
            background-color: white;
            padding: 10px 0px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        /* Barra decorativa gris delgada con borde rojo inferior */
        .decor-bar {
            background-color: #EEEEEE; 
            border-bottom: 5px solid #E30613; 
            height: 30px; 
            width: 100%;
            border-radius: 5px;
            margin-bottom: 10px;
        }

        /* Centrado del título principal */
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

    # 3. ENCABEZADO: LOGO DE ETERNIT CENTRADO (Nitidez original)
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    izq, logo_centro, der = st.columns([1.5, 2, 1.5])
    with logo_centro:
        # Usamos el archivo de alta resolución para el panel interno
        # Al usar use_container_width=True dentro de una columna controlada, se mantiene nítido
        st.image("logo-eternit-400x150-1.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # BARRA DECORATIVA (Gris con borde rojo)
    st.markdown('<div class="decor-bar"></div>', unsafe_allow_html=True)

    # NUEVO TÍTULO CENTRADO
    st.markdown('<h1 class="main-title">🚛 Smart Picking & Logistic Guide</h1>', unsafe_allow_html=True)

    # 4. SIDEBAR Y LÓGICA DE CARGA
    with st.sidebar:
        st.header("Entrada de Datos")
        pedido_raw = st.text_input("Ingrese cantidad de Teja de # 4", value="0")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
    
    # Parámetros técnicos para Teja #4
    cantidad = int(pedido_raw) if pedido_raw.isdigit() else 0
    PAQUETE = 130
    MAX_PAQUETES = 20
    MAX_SALDO_UNIDAD = 60
    CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (20 * MAX_SALDO_UNIDAD)

    if cantidad > CAPACIDAD_TOTAL:
        st.error(f"⚠️ El pedido excede la capacidad ({CAPACIDAD_TOTAL} unidades).")
        st.stop()

    # Cálculos de distribución
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
