import streamlit as st
import re

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
            st.markdown(f"""
                <div style="background-color: #E0E0E0; padding: 30px; border-radius: 15px; border-top: 8px solid #E30613; text-align: center;">
                    <h1 style="color: #E30613; margin-bottom: 0; font-family: Arial Black;">ETERNIT</h1>
                    <p style="color: #1A3A5A; font-weight: bold;">SISTEMA DE PICKING</p>
                </div>
            """, unsafe_allow_html=True)
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
        return False
    return True

if login():
    # 2. ESTILOS CSS
    st.markdown("""
    <style>
        .header-container { background-color: white; padding: 10px 0px; display: flex; justify-content: center; align-items: center; }
        .decor-bar { background-color: #EEEEEE; border-bottom: 5px solid #E30613; height: 30px; width: 100%; border-radius: 5px; margin-bottom: 10px; }
        .main-title { text-align: center; color: #1A3A5A; font-family: sans-serif; margin-bottom: 30px; }
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 15px; font-weight: bold; border-radius: 10px 10px 0 0; }
        .celda { background: #27ae60; color: white; text-align: center; padding: 12px; margin: 4px; border-radius: 6px; font-weight: bold; }
        .saldo { background: #f1c40f; color: black; padding: 12px; margin: 4px; border-radius: 6px; text-align: center; font-weight: bold; }
        .info-box { background-color: #f8f9fa; padding: 15px; border-left: 5px solid #1A3A5A; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

    # 3. ENCABEZADO
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    izq, logo_centro, der = st.columns([1.5, 2, 1.5])
    with logo_centro:
        st.image("logo-eternit-400x150-1.png", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="decor-bar"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🚛 Smart Picking & Logistic Guide</h1>', unsafe_allow_html=True)

    # 4. PROCESADOR DE TEXTO (PARSER) EN SIDEBAR
    with st.sidebar:
        st.header("📥 Entrada de Datos")
        texto_pegado = st.text_area("Pegue aquí los datos del pedido:", 
                                   placeholder="Ej: 1321786 TEJA FLEXIFORTE #6 VILLAPINZON 3300 unidades 100 ton",
                                   height=150)
        
        # Variables por defecto
        codigo, material, zona, unidades, tonelaje = "---", "---", "---", 0, "0"

        if texto_pegado:
            # Lógica para extraer números y palabras
            numeros = re.findall(r'\d+', texto_pegado)
            if len(numeros) >= 2:
                codigo = numeros[0]
                unidades = int(numeros[-2]) # Penúltimo número suele ser cantidad
                tonelaje = numeros[-1]      # Último número suele ser peso
            
            # Intentar extraer descripción (Texto entre código y unidades)
            palabras = texto_pegado.split()
            if len(palabras) > 2:
                material = " ".join(palabras[1:4]) # Toma las primeras palabras tras el código
                zona = palabras[4] if len(palabras) > 4 else "No detectada"

        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

    # 5. TABLAS DE INFORMACIÓN (Lo que pediste)
    col_info1, col_info2 = st.columns([1, 1])
    
    with col_info1:
        st.subheader("📋 Registro Plano")
        # Tabla en blanco con el formato pegado
        st.markdown(f"""
        <div style="background-color: white; border: 1px solid #ddd; padding: 15px; font-family: monospace; font-size: 18px;">
            {codigo} | {material} | {zona} | {unidades} UNID | {tonelaje} TON
        </div>
        """, unsafe_allow_html=True)

    with col_info2:
        st.subheader("🔍 Desglose de Carga")
        # Tabla segregada a la izquierda
        st.markdown(f"""
        <div class="info-box">
            <p><b>Código:</b> {codigo}</p>
            <p><b>Material:</b> {material}</p>
            <p><b>Zona:</b> {zona}</p>
            <p><b>Cantidad:</b> {unidades} Unidades</p>
            <p><b>Tonelaje:</b> {tonelaje} Toneladas</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # 6. LÓGICA DE DISTRIBUCIÓN (MULA)
    PAQUETE = 130
    MAX_PAQUETES = 20
    MAX_SALDO_UNIDAD = 60
    CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (20 * MAX_SALDO_UNIDAD)

    if unidades > CAPACIDAD_TOTAL:
        st.error(f"⚠️ El pedido de {unidades} unidades excede la capacidad.")
    else:
        paquetes_ok = min(unidades // PAQUETE, MAX_PAQUETES)
        sobrante = unidades - (paquetes_ok * PAQUETE)
        saldos_lista = []
        while sobrante > 0:
            if sobrante >= MAX_SALDO_UNIDAD:
                saldos_lista.append(MAX_SALDO_UNIDAD); sobrante -= MAX_SALDO_UNIDAD
            else:
                saldos_lista.append(sobrante); sobrante = 0

        s_izq, s_der = saldos_lista[0::2], saldos_lista[1::2]
        p_izq, p_der = paquetes_ok // 2 + paquetes_ok % 2, paquetes_ok // 2

        # Gráfico del camión
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        for i in range(10):
            r1, r2, r3, r4 = st.columns([1, 1, 1, 1])
            with r1: st.markdown(f'<div class="saldo">{s_izq[i] if i < len(s_izq) else ""}</div>', unsafe_allow_html=True)
            with r2: st.markdown(f'<div class="celda">{"130" if i < p_izq else ""}</div>', unsafe_allow_html=True)
            with r3: st.markdown(f'<div class="celda">{"130" if i < p_der else ""}</div>', unsafe_allow_html=True)
            with r4: st.markdown(f'<div class="saldo">{s_der[i] if i < len(s_der) else ""}</div>', unsafe_allow_html=True)
