```python
import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# Base de datos de productos
PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

st.set_page_config(page_title="Simulador de Cargue", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


# -------- LOGIN --------
if not st.session_state.autenticado:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)

        st.image("ETERNIT LOGOS.webp", width=180)

        st.markdown(
        """
        <h3 style="
        text-align:center;
        margin-top:10px;
        color:#E30613;
        font-weight:700;
        font-size:24px;
        ">
        Simulador de Cargue
        </h3>
        """,
        unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

        usuario = st.text_input("Correo electrónico").upper()
        clave = st.text_input("Contraseña", type="password")

        if st.button("Ingresar al Sistema", use_container_width=True):
            if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Acceso denegado")


# -------- SISTEMA --------
else:

    st.markdown(
    """
    <div style="
    background-color:#E30613;
    padding:12px;
    border-radius:8px;
    text-align:center;
    color:white;
    font-weight:bold;
    font-size:20px;
    margin-bottom:15px;
    ">
    SIMULADOR DE CARGUE - LOGÍSTICA ETERNIT
    </div>
    """,
    unsafe_allow_html=True
    )

    st.markdown("""
    <style>
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 15px; font-weight: bold; border-radius: 8px 8px 0 0; margin-bottom:10px; border-bottom: 5px solid #bdc3c7; }
        .paquete-v { background: #27ae60; color: white; text-align: center; padding: 12px; margin: 4px; border-radius: 5px; font-size: 13px; font-weight: bold; border: 1px solid #1e8449; }
        .paquete-h { background: #2980b9; color: white; text-align: center; padding: 15px; margin: 10px auto; border-radius: 6px; font-weight: bold; border: 2px dashed #ecf0f1; width: 80%; }
        .saldo-box { background: #f1c40f; color: #2c3e50; text-align: center; padding: 8px; margin: 4px; border-radius: 5px; font-size: 11px; font-weight: 800; border: 1px solid #d4ac0d; line-height: 1.2; }
        .stMetric { background: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 5px solid #E30613; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Carga de Pedido")

        raw_data = st.text_area(
            "Pegue aquí el pedido:",
            height=300,
            placeholder="Ejemplo:\nTEJA FLEXIFORTE #5 900\nTEJA PERFIL #4 150"
        )

        if st.button("Limpiar Datos"):
            st.session_state.raw_data = ""
            st.rerun()

    pedido_items = []
    peso_total_pedido = 0

    if raw_data:

        lines = raw_data.strip().split('\n')

        for line in lines:

            line_upper = line.upper().strip()

            if not line_upper:
                continue

            match_ref = re.search(r'#(\d+)', line_upper)

            if match_ref:

                num_ref = match_ref.group(1)

                if num_ref in PRODUCTOS_BASE:

                    numeros = re.findall(r'\d+', line_upper.replace(f"#{num_ref}", ""))

                    if numeros:

                        cant = int(numeros[-1])
                        info = PRODUCTOS_BASE[num_ref]

                        nombre_mostrar = f"TEJA #{num_ref}"

                        if "FLEXIFORTE" in line_upper:
                            nombre_mostrar = f"FLEX. #{num_ref}"

                        pedido_items.append({
                            "tipo": nombre_mostrar,
                            "cant": cant,
                            "peso": cant * info["peso"],
                            "ref": num_ref
                        })

                        peso_total_pedido += cant * info["peso"]

    if pedido_items:

        vh_asignado = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])

        st.markdown(f"### 🚛 Vehículo Sugerido: {vh_asignado['tipo']}")

        c1, c2, c3 = st.columns(3)

        c1.metric("Peso Total Estimado", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Capacidad Vehículo", f"{vh_asignado['capacidad_max']:,.0f} kg")

        largo_req = max([PRODUCTOS_BASE[i['ref']]['largo_ft'] for i in pedido_items])

        c3.metric("Largo de Carga", f"{largo_req} ft")

        pedido_sorted = sorted(pedido_items, key=lambda x: PRODUCTOS_BASE[x['ref']]['largo_ft'], reverse=True)

        mapa_vertical = []
        saldos = []

        MAX_SALDO_UNIDADES = 60

        for item in pedido_sorted:

            paq_tam = PRODUCTOS_BASE[item['ref']]['paquete']

            completos = item["cant"] // paq_tam
            sobra_total = item["cant"] % paq_tam

            for _ in range(completos):
                mapa_vertical.append({"label": item["tipo"], "cant": paq_tam})

            while sobra_total > 0:

                if sobra_total > MAX_SALDO_UNIDADES:
                    saldos.append({"label": item["tipo"], "cant": MAX_SALDO_UNIDADES})
                    sobra_total -= MAX_SALDO_UNIDADES
                else:
                    saldos.append({"label": item["tipo"], "cant": sobra_total})
                    sobra_total = 0

        st.markdown("---")
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        paquetes_render = list(mapa_vertical)

        atravesado = paquetes_render.pop() if len(paquetes_render) % 2 != 0 else None

        rows_completos = [paquetes_render[i:i+2] for i in range(0, len(paquetes_render), 2)]
        saldos_render = list(saldos)

        for row in rows_completos:

            cols = st.columns([1,1.5,1.5,1])

            with cols[0]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

            with cols[1]:
                st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)

            with cols[2]:
                if len(row) > 1:
                    st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)

            with cols[3]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        while saldos_render:

            cols_ex = st.columns([1,1.5,1.5,1])

            with cols_ex[0]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

            with cols_ex[3]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        if atravesado:
            st.markdown(f'<div class="paquete-h">📦 PAQUETE COMPLETO TRASERO<br>{atravesado["label"]} ({atravesado["cant"]} UND)</div>', unsafe_allow_html=True)

    else:
        st.info("Esperando datos del pedido... Copia y pega el contenido del pedido en la barra lateral.")
```
