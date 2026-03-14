import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------

st.set_page_config(
    page_title="Simulador de Cargue 2D",
    page_icon="🚛",
    layout="wide"
)

USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# -----------------------------
# BASE DE PRODUCTOS
# -----------------------------

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130},
    "5": {"peso": 14.77, "paquete": 130},
    "6": {"peso": 17.72, "paquete": 130},
    "8": {"peso": 23.63, "paquete": 130},
    "10": {"peso": 29.54, "paquete": 100},
}

# -----------------------------
# VEHÍCULOS
# -----------------------------

VEHICULOS = [
    {"tipo": "TURBO", "capacidad": 5000, "largo": 20, "ancho": 4},
    {"tipo": "SENCILLO", "capacidad": 10000, "largo": 24, "ancho": 5},
    {"tipo": "DOBLE TROQUE", "capacidad": 18000, "largo": 28, "ancho": 6},
    {"tipo": "CUATRO MANOS", "capacidad": 22000, "largo": 32, "ancho": 6},
    {"tipo": "MULA", "capacidad": 34000, "largo": 40, "ancho": 8},
]

# -----------------------------
# LOGIN
# -----------------------------

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.image("logo-eternit-400x150-1.png", use_container_width=True)
        st.markdown(
            "<h1 style='text-align:center;color:#1A3A5A;font-size:40px'>Simulador de Cargue 2D</h1>",
            unsafe_allow_html=True,
        )

        usuario = st.text_input("Correo")
        clave = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):
            if usuario.upper() == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

# -----------------------------
# APP
# -----------------------------

else:

    st.title("🚛 Simulador Logístico 2D")

    with st.sidebar:
        st.header("Pedido")
        raw = st.text_area("Pegue el pedido", height=250)

    pedido = []
    peso_total = 0

    if raw:

        lines = raw.strip().split("\n")

        for line in lines:
            line = line.upper().strip()
            match_ref = re.search(r"#(\d+)", line)

            if match_ref:
                num_ref = match_ref.group(1)

                if num_ref in PRODUCTOS_BASE:
                    nums = re.findall(r"\d+", line.replace(f"#{num_ref}", ""))

                    if nums:
                        cant = int(nums[-1])
                        peso = cant * PRODUCTOS_BASE[num_ref]["peso"]

                        pedido.append({"ref": num_ref, "cantidad": cant})
                        peso_total += peso

    if pedido:

        # Escoger Vehículo
        vh = next((v for v in VEHICULOS if v["capacidad"] >= peso_total), VEHICULOS[-1])

        toneladas = peso_total / 1000

        porcentaje = (peso_total / vh["capacidad"]) * 100

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Peso total (kg)", f"{peso_total:,.0f}")
        c2.metric("Toneladas", f"{toneladas:.2f}")
        c3.metric("Vehículo sugerido", vh["tipo"])
        c4.metric("% Ocupación", f"{porcentaje:.1f}%")

        # Preparar data para 2D
        paquetes = []
        for item in pedido:
            paq_size = PRODUCTOS_BASE[item["ref"]]["paquete"]
            completos = item["cantidad"] // paq_size
            for i in range(completos):
                paquetes.append(item)

        # Representación 2D
        fig = go.Figure()

        # Dibujar contorno del camión
        fig.add_shape(
            type="rect",
            x0=0,
            y0=0,
            x1=vh["largo"],
            y1=vh["ancho"],
            line=dict(color="black", width=3),
        )

        # Añadir cada paquete como rectángulo
        row = 0
        col = 0
        unit = 3  # espacio base por paquete

        for i, p in enumerate(paquetes):

            # posición del rectángulo
            x0 = col * unit
            y0 = row * unit
            x1 = x0 + (unit - 0.2)
            y1 = y0 + (unit - 0.2)

            fig.add_shape(
                type="rect",
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                fillcolor="red",
                line=dict(color="black"),
            )

            # avanzar filas
            col += 1
            if (col + 1) * unit > vh["largo"]:
                col = 0
                row += 1

        fig.update_layout(
            title="Plano de cargue 2D (vista superior)",
            xaxis=dict(title="Largo del vehículo", range=[0, vh["largo"] + 1]),
            yaxis=dict(title="Ancho del vehículo", range=[0, vh["ancho"] + 1]),
            height=500,
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Pega un pedido para generar la simulación.")
