import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
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
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

st.set_page_config(page_title="Smart Picking PRO", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("ETERNIT LOGOS.webp", use_container_width=True)
        usuario = st.text_input("Correo electrónico").upper()
        clave = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Acceso denegado")
else:
    st.markdown("""
    <style>
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 10px; font-weight: bold; border-radius: 5px; margin-bottom:10px; }
        .paquete-v { background: #27ae60; color: white; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; height: 80px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
        .paquete-h { background: #2980b9; color: white; text-align: center; padding: 15px; margin: 5px; border-radius: 4px; font-weight: bold; border: 2px dashed white; }
        .saldo-box { background: #f1c40f; color: black; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; font-weight: bold; height: 80px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
        .stMetric { background: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid #E30613; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Carga de Pedido")
        raw_data = st.text_area("Pegue aquí el pedido:", height=250)
        if st.button("Limpiar Datos"):
            st.rerun()

    pedido_items = []
    peso_total_pedido = 0
    
    if raw_data:
        lines = raw_data.strip().split('\n')
        for line in lines:
            line_upper = line.upper().strip()
            if not line_upper: continue
            match_ref = re.search(r'#(\d+)', line_upper)
            if match_ref:
                num_ref = match_ref.group(1)
                if num_ref in PRODUCTOS_BASE:
                    numeros = re.findall(r'\d+', line_upper.replace(f"#{num_ref}", ""))
                    if numeros:
                        cant = int(numeros[-1])
                        info = PRODUCTOS_BASE[num_ref]
                        nombre_mostrar = f"TEJA FLEX. #{num_ref}" if "FLEX" in line_upper else f"TEJA #{num_ref}"
                        pedido_items.append({"tipo": nombre_mostrar, "cant": cant, "peso": cant * info["peso"], "ref": num_ref})
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        vh_asignado = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        st.markdown(f"### 🚛 Vehículo Sugerido: {vh_asignado['tipo']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Capacidad VH", f"{vh_asignado['capacidad_max']:,.0f} kg")
        largo_req = max([PRODUCTOS_BASE[i['ref']]['largo_ft'] for i in pedido_items])
        c3.metric("Largo Requerido", f"{largo_req} ft")

        # --- CORRECCIÓN DE LÓGICA DE DISTRIBUCIÓN ---
        pedido_sorted = sorted(pedido_items, key=lambda x: PRODUCTOS_BASE[x['ref']]['largo_ft'], reverse=True)
        mapa_vertical = []
        saldos = []
        
        for item in pedido_sorted:
            paq_tam = PRODUCTOS_BASE[item['ref']]['paquete']
            num_paquetes = item["cant"] // paq_tam
            sobrante_unidades = item["cant"] % paq_tam
            
            for _ in range(num_paquetes):
                mapa_vertical.append({"label": item["tipo"], "cant": paq_tam})
            
            if sobrante_unidades > 0:
                saldos.append({"label": item["tipo"], "cant": sobrante_unidades})

        st.markdown("---")
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        paquetes_render = list(mapa_vertical)
        atravesado = None
        # Si hay un número impar de paquetes completos, el último va horizontal
        if len(paquetes_render) % 2 != 0:
            atravesado = paquetes_render.pop()

        rows = [paquetes_render[i:i+2] for i in range(0, len(paquetes_render), 2)]
        saldos_render = list(saldos)

        # Renderizado de filas
        for row in rows:
            cols = st.columns(4)
            with cols[0]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]:
                if len(row) > 1:
                    st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)
            with cols[3]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)

        # Saldos restantes si no hubo suficientes paquetes verdes para acompañarlos
        if saldos_render:
            while saldos_render:
                cols_ex = st.columns(4)
                with cols_ex[0]:
                    if saldos_render:
                        s = saldos_render.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)
                with cols_ex[3]:
                    if saldos_render:
                        s = saldos_render.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)

        if atravesado:
            st.markdown(f'<div class="paquete-h">📦 PAQUETE HORIZONTAL TRASERO<br>{atravesado["label"]} ({atravesado["cant"]})</div>', unsafe_allow_html=True)
    else:
        st.info("Pega los datos del pedido para ver el desglose.")
