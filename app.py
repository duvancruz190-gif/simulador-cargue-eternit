import streamlit as st
import base64

# 1. CONFIGURACIÓN DE SEGURIDAD
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

st.set_page_config(page_title="Smart Picking & Logistic Guide", layout="wide")

# Función de Validación de Acceso
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        # --- NUEVO CSS PARA DISEÑO MINIMALISTA Y SUTIL ---
        # Este CSS elimina barras, centra todo y da estilos limpios
        st.markdown("""
            <style>
            /* Elimina el header por defecto de Streamlit */
            header { visibility: hidden; }
            
            /* Contenedor principal de login centrado */
            .stApp > div {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin-top: 0;
            }
            
            /* Caja de login sutil y flotante */
            .login-box {
                background-color: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
                margin-top: -100px; /* Ajuste para centrar visualmente */
            }
            
            /* Estilo del botón */
            .stButton>button {
                width: 100%;
                background-color: #E30613;
                color: white;
                border-radius: 6px;
                border: none;
                font-weight: bold;
                height: 3em;
            }
            </style>
        """, unsafe_allow_html=True)

        # Usamos columnas solo para forzar el centrado
        col1, col2, col3 = st.columns([1, 1.2, 1])
        
        with col2:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            
            # --- EL LOGO: SUTIL, PEQUEÑO Y NÍTIDO ---
            # Para garantizar nitidez total, cargamos la imagen en base64
            # Asegúrate que el archivo 'Elementia.png' esté en tu carpeta.
            # 'Elementia.png' es la imagen que tiene el logo original nítido.
            with open("Elementia.png", "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode()
            
            # El width=200 asegura que se vea pequeño y sutil, sin estirarse.
            st.markdown(f'<img src="data:image/png;base64,{encoded_image}" width="200" style="margin-bottom: 20px;">', unsafe_allow_html=True)
            
            st.markdown('<p style="color: #1A3A5A; font-weight: bold; margin-bottom: 25px;">SISTEMA DE PICKING</p>', unsafe_allow_html=True)
            
            st.subheader("Inicie sesión para continuar")
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            
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
    # --- RESTO DEL CÓDIGO (Sin cambios, ya que aquí sí se quiere el header) ---
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

    # 3. ENCABEZADO INTERNO: LOGO PEQUEÑO Y NÍTIDO
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    izq, logo_centro, der = st.columns([1.5, 2, 1.5])
    with logo_centro:
        # Usamos use_container_width=True aquí para que el logo se ajuste 
        # a la columna central (que es más estrecha), manteniendo la nitidez.
        st.image("Elementia.png", use_container_width=True)
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
