import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# Base de datos simplificada (El buscador ahora es inteligente)
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
    # 2. ESTILOS CSS
    st.markdown("""
    <style>
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 10px; font-weight: bold; border-radius: 5px; margin-bottom:10px; }
        .paquete-v { background: #27ae60; color: white; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; }
        .paquete-h { background: #2980b9; color: white; text-align: center; padding: 15px; margin: 5px; border-radius: 4px; font-weight: bold; border: 2px dashed white; }
        .saldo-box { background: #f1c40f; color: black; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .stMetric { background: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid #E30613; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Carga de Pedido")
        raw_data = st.text_area("Pegue aquí el pedido:", height=250, placeholder="TEJA FLEXIFORTE #5 900")
        if st.button("Limpiar Datos"):
            st.rerun()

    # --- LÓGICA DE PROCESAMIENTO ULTRA-ROBUSTA ---
    pedido_items = []
    peso_total_pedido = 0
    
    if raw_data:
        lines = raw_data.strip().split('\n')
        for line in lines:
            line_upper = line.upper().strip()
            if not line_upper: continue
            
            # Buscamos el número de teja (#4, #5, etc.) y la cantidad
            # Esta expresión busca: palabra TEJA + cualquier texto + # + número de referencia + espacio + cantidad
            match_ref = re.search(r'#(\d+)', line_upper)
            
            if match_ref:
                num_ref = match_ref.group(1) # Extrae el '5' de '#5'
                if num_ref in PRODUCTOS_BASE:
                    # Buscamos la cantidad: es el número más grande al final o después de la referencia
                    numeros = re.findall(r'\d+', line_upper.replace(f"#{num_ref}", ""))
                    if numeros:
                        cant = int(numeros[-1]) # Tomamos el último número de la línea (usualmente la cantidad)
                        info = PRODUCTOS_BASE[num_ref]
                        
                        nombre_mostrar = f"TEJA #{num_ref}"
                        if "FLEXIFORTE" in line_upper: nombre_mostrar = f"TEJA FLEX. #{num_ref}"
                        
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

        # DISTRIBUCIÓN
        pedido_sorted = sorted(pedido_items, key=lambda x: PRODUCTOS_BASE[x['ref']]['largo_ft'], reverse=True)
        mapa_vertical = []
        saldos = []
        
        for item in pedido_sorted:
            paq_tam = PRODUCTOS_BASE[item['ref']]['paquete']
            completos = item["cant"] // paq_tam
            sobra = item["cant"] % paq_tam
            for _ in range(completos):
                mapa_vertical.append({"label": item["tipo"], "cant": paq_tam})
            if sobra > 0:
                saldos.append({"label": item["tipo"], "cant": sobra})

        # MAPA VISUAL
        st.markdown("---")
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        paquetes_render = list(mapa_vertical)
        atravesado = paquetes_render.pop() if len(paquetes_render) % 2 != 0 else None
        rows = [paquetes_render[i:i+2] for i in range(0, len(paquetes_render), 2)]
        saldos_render = list(saldos)

        for row in rows:
            cols = st.columns(4)
            with cols[0]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]:
                if len(row) > 1: st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)
            with cols[3]:
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)

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
