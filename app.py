import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------

st.set_page_config(
    page_title="Simulador de Cargue",
    page_icon="🚛",
    layout="wide"
)

USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# -----------------------------
# BASE PRODUCTOS
# -----------------------------

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

# -----------------------------
# VEHÍCULOS
# -----------------------------

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

# -----------------------------
# ESTADO LOGIN
# -----------------------------

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ==========================================================
# LOGIN
# ==========================================================

if not st.session_state.autenticado:

    col1, col2, col3 = st.columns([1,1.4,1])

    with col2:

        st.image("logo-eternit-400x150-1.png", use_container_width=True)

        st.markdown(
        """
        <h1 style='text-align:center;
        color:#E30613;
        font-weight:800;
        font-size:26px;
        margin-top:10px'>
        Simulador de Cargue
        </h1>
        """,
        unsafe_allow_html=True
        )

        with st.container(border=True):

            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")

            if st.button("Ingresar al Sistema", use_container_width=True):

                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()

                else:
                    st.error("Credenciales incorrectas")

# ==========================================================
# SISTEMA
# ==========================================================

else:

    st.markdown("""
    <div style="
    background:#E30613;
    padding:12px;
    border-radius:8px;
    text-align:center;
    color:white;
    font-weight:bold;
    font-size:22px;
    margin-bottom:20px;
    ">
    🚛 SIMULADOR DE CARGUE - LOGÍSTICA
    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

    with st.sidebar:

        st.header("📋 Pedido")

        raw_data = st.text_area(
            "Pegue el pedido aquí",
            height=300,
            placeholder="Ejemplo:\nTEJA FLEXIFORTE #5 900\nTEJA PERFIL #4 150"
        )

        if st.button("Limpiar"):
            st.rerun()

# ==========================================================
# PROCESAMIENTO PEDIDO
# ==========================================================

    pedido_items = []
    peso_total_pedido = 0

    if raw_data:

        lines = raw_data.strip().split("\n")

        for line in lines:

            line_upper = line.upper().strip()

            match_ref = re.search(r'#(\d+)', line_upper)

            if match_ref:

                num_ref = match_ref.group(1)

                if num_ref in PRODUCTOS_BASE:

                    numeros = re.findall(r'\d+', line_upper.replace(f"#{num_ref}", ""))

                    if numeros:

                        cant = int(numeros[-1])
                        info = PRODUCTOS_BASE[num_ref]

                        nombre = f"FLEX. #{num_ref}"

                        pedido_items.append({
                            "tipo": nombre,
                            "cant": cant,
                            "peso": cant * info["peso"],
                            "ref": num_ref
                        })

                        peso_total_pedido += cant * info["peso"]

# ==========================================================
# RESULTADOS
# ==========================================================

    if pedido_items:

        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])

        st.subheader(f"🚛 Vehículo sugerido: {vh['tipo']}")

        c1, c2, c3 = st.columns(3)

        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Capacidad Vehículo", f"{vh['capacidad_max']:,.0f} kg")

        largo_planchon = vh["largo_planchon_ft"]
        c3.metric("Largo Planchón", f"{largo_planchon} ft")

        st.divider()

        st.markdown('<div style="background:#1A3A5A;color:white;text-align:center;padding:10px;border-radius:8px">FRENTE DEL VEHÍCULO</div>', unsafe_allow_html=True)

# ==========================================================
# LÓGICA REAL DE CARGUE
# ==========================================================

        mapa_vertical = []
        saldos = []

        pasos_usados = 0

        for item in pedido_items:

            ref = item["ref"]
            info = PRODUCTOS_BASE[ref]

            largo = info["largo_ft"]
            paquete = info["paquete"]

            paquetes = item["cant"] // paquete
            sobrante = item["cant"] % paquete

            for _ in range(paquetes):

                if pasos_usados + largo <= largo_planchon:

                    mapa_vertical.append({"label": item["tipo"], "cant": paquete})
                    pasos_usados += largo

            while sobrante > 0:

                cant = min(sobrante,60)

                saldos.append({
                    "label": item["tipo"],
                    "cant": cant
                })

                sobrante -= cant

# ==========================================================
# PAQUETE ATRAVESADO
# ==========================================================

        pasos_restantes = largo_planchon - pasos_usados
        atravesado = None

        if pasos_restantes == 4 and mapa_vertical:
            atravesado = mapa_vertical.pop()

# ==========================================================
# RENDER
# ==========================================================

        filas = [mapa_vertical[i:i+2] for i in range(0,len(mapa_vertical),2)]

        for fila in filas:

            col1,col2,col3,col4 = st.columns([1,2,2,1])

            with col2:
                st.markdown(f"<div style='background:#27ae60;color:white;padding:10px;text-align:center;border-radius:6px'>{fila[0]['label']}<br>{fila[0]['cant']}</div>", unsafe_allow_html=True)

            if len(fila)>1:
                with col3:
                    st.markdown(f"<div style='background:#27ae60;color:white;padding:10px;text-align:center;border-radius:6px'>{fila[1]['label']}<br>{fila[1]['cant']}</div>", unsafe_allow_html=True)

# ----------------------------------------------------------

        if atravesado:

            st.markdown(
            f"<div style='background:#2980b9;color:white;text-align:center;padding:12px;border-radius:6px;margin-top:10px'>PAQUETE ATRAVESADO<br>{atravesado['label']} ({atravesado['cant']})</div>",
            unsafe_allow_html=True
            )

# ----------------------------------------------------------

        if saldos:

            st.divider()
            st.subheader("Saldos sobre paquetes")

            cols = st.columns(6)

            for i,s in enumerate(saldos):

                with cols[i%6]:

                    st.markdown(
                    f"<div style='background:#f1c40f;color:black;padding:6px;text-align:center;border-radius:5px'>{s['label']}<br>{s['cant']}</div>",
                    unsafe_allow_html=True
                    )

    else:

        st.info("Pegue un pedido en el panel izquierdo para generar la simulación.")
