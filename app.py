import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue", page_icon="🚛", layout="wide")

USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "filas_max": 2},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "filas_max": 3},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "filas_max": 4},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "filas_max": 5},
    {"tipo": "MULA", "capacidad_max": 34000, "filas_max": 6}, # Límite físico real
]

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    # --- LOGIN ---
    st.markdown("<style>div.stButton > button {background-color:#E30613; color:white; font-weight:bold;}</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>Simulador de Cargue</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            usuario = st.text_input("Correo").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Error")
else:
    # --- SISTEMA ---
    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Pedido")
        raw_data = st.text_area("Pegue el pedido aquí", height=300)
        if st.button("Limpiar"): st.rerun()

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
                        pedido_items.append({"tipo": f"REF #{num_ref}", "cant": cant, "peso": cant * info["peso"], "ref": num_ref})
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        # VALIDACIÓN DE CAPACIDAD PESO
        if peso_total_pedido > VEHICULOS[-1]["capacidad_max"]:
            st.error(f"❌ EL PEDIDO EXCEDE LA CAPACIDAD DE CARGA (Máx {VEHICULOS[-1]['capacidad_max']} kg)")
            st.stop()

        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        st.subheader(f"🚛 Vehículo: {vh['tipo']}")

        # LÓGICA DE DISTRIBUCIÓN
        mapa_paquetes = []
        saldos_lista = []
        
        for item in sorted(pedido_items, key=lambda x: int(x['ref']), reverse=True):
            paq_size = PRODUCTOS_BASE[item['ref']]['paquete']
            completos = item["cant"] // paq_size
            sobra = item["cant"] % paq_size
            for _ in range(completos): mapa_paquetes.append(item["tipo"])
            if sobra > 0:
                if sobra > 60:
                    saldos_lista.append({"label": item["tipo"], "cant": sobra // 2})
                    saldos_lista.append({"label": item["tipo"], "cant": sobra - (sobra // 2)})
                else:
                    saldos_lista.append({"label": item["tipo"], "cant": sobra})

        rows = [mapa_paquetes[i:i+2] for i in range(0, len(mapa_paquetes), 2)]

        # VALIDACIÓN DE ESPACIO FÍSICO
        if len(rows) > vh["filas_max"]:
            st.error(f"⚠️ EL PEDIDO NO CABE FÍSICAMENTE EN UN {vh['tipo']}. (Requiere {len(rows)} filas, Máx: {vh['filas_max']})")
            st.stop()

        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        saldos_render = list(saldos_lista)
        for row in rows:
            cols = st.columns([1, 1.5, 1.5, 1])
            with cols[0]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div class="paquete-v">{row[0]}<br>(PAQUETE)</div>', unsafe_allow_html=True)
            with cols[2]:
                if len(row) > 1:
                    st.markdown(f'<div class="paquete-v">{row[1]}<br>(PAQUETE)</div>', unsafe_allow_html=True)
            with cols[3]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
        
        # Saldos restantes si los hay
        if saldos_render:
            st.write("Saldos adicionales en parte trasera:")
            c_s = st.columns(len(saldos_render) if len(saldos_render) < 5 else 4)
            for i, s in enumerate(saldos_render):
                with c_s[i % 4]:
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
