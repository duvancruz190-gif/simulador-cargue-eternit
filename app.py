import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS (SEGÚN TU TABLA)
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
        .paquete-v { background: #27ae60; color: white; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; height: 90px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
        .paquete-h { background: #2980b9; color: white; text-align: center; padding: 15px; margin: 5px; border-radius: 4px; font-weight: bold; border: 2px dashed white; }
        .saldo-box { background: #f1c40f; color: black; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; font-weight: bold; height: 90px; display: flex; align-items: center; justify-content: center; flex-direction: column; border: 1px solid #d4ac0d; }
        .pico-box { background: #E30613; color: white; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 11px; height: 90px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
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
                        nombre = f"TEJA #{num_ref}"
                        if "FLEX" in line_upper: nombre = f"TEJA FLEX. #{num_ref}"
                        pedido_items.append({"tipo": nombre, "cant": cant, "peso": cant * info["peso"], "ref": num_ref})
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        vh_asignado = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        st.markdown(f"### 🚛 Vehículo Sugerido: {vh_asignado['tipo']}")
        
        # --- LÓGICA DE DISTRIBUCIÓN BASADA EN TU IMAGEN ---
        mapa_vertical = []
        saldos_60 = []
        picos_sueltos = []
        
        for item in pedido_items:
            info = PRODUCTOS_BASE[item['ref']]
            cant_actual = item["cant"]
            
            # 1. Paquetes grandes (130 o 100)
            num_paquetes = cant_actual // info["paquete"]
            residuo = cant_actual % info["paquete"]
            
            for _ in range(num_paquetes):
                mapa_vertical.append({"label": item["tipo"], "cant": info["paquete"]})
            
            # 2. Manejo de Saldos (Regla de 60)
            if residuo > 0:
                num_saldos_60 = residuo // 60
                pico = residuo % 60
                
                for _ in range(num_saldos_60):
                    saldos_60.append({"label": item["tipo"], "cant": 60})
                
                if pico > 0:
                    picos_sueltos.append({"label": item["tipo"], "cant": pico})

        # --- RENDERIZADO VISUAL ---
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        paquetes_render = list(mapa_vertical)
        atravesado = paquetes_render.pop() if len(paquetes_render) % 2 != 0 else None
        rows = [paquetes_render[i:i+2] for i in range(0, len(paquetes_render), 2)]
        
        todos_los_saldos = saldos_60 + picos_sueltos

        for row in rows:
            cols = st.columns(4)
            with cols[0]:
                if todos_los_saldos:
                    s = todos_los_saldos.pop(0)
                    clase = "saldo-box" if s["cant"] == 60 else "pico-box"
                    st.markdown(f'<div class="{clase}">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]:
                if len(row) > 1: st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)
            with cols[3]:
                if todos_los_saldos:
                    s = todos_los_saldos.pop(0)
                    clase = "saldo-box" if s["cant"] == 60 else "pico-box"
                    st.markdown(f'<div class="{clase}">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)

        # Saldos extra si sobran
        while todos_los_saldos:
            cols_ex = st.columns(4)
            with cols_ex[0]:
                if todos_los_saldos:
                    s = todos_los_saldos.pop(0)
                    clase = "saldo-box" if s["cant"] == 60 else "pico-box"
                    st.markdown(f'<div class="{clase}">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)
            with cols_ex[3]:
                if todos_los_saldos:
                    s = todos_los_saldos.pop(0)
                    clase = "saldo-box" if s["cant"] == 60 else "pico-box"
                    st.markdown(f'<div class="{clase}">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)

        if atravesado:
            st.markdown(f'<div class="paquete-h">📦 PAQUETE HORIZONTAL TRASERO<br>{atravesado["label"]} ({atravesado["cant"]})</div>', unsafe_allow_html=True)
    else:
        st.info("Pega el pedido para procesar según la tabla técnica.")
