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
    "16": {"peso": 47.26, "paquete": 50, "largo_ft": 16}, # Añadida por si se usa en pedidos
}

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<style>div.stButton > button { background-color:#E30613; color:white; font-weight:bold; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        st.title("🚛 Acceso al Sistema")
        with st.container(border=True):
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar al Sistema", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Credenciales incorrectas")
else:
    # --- INTERFAZ PRINCIPAL ---
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - LOGÍSTICA</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; min-height:80px; display:flex; align-items:center; justify-content:center; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #7d6608; min-height:80px; display:flex; align-items:center; justify-content:center; }
    .metric-container { background:#f0f2f6; padding:15px; border-radius:10px; text-align:center; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Entrada de Pedido")
        st.info("Pegue el pedido desde Excel o texto plano. Ej: TEJA #10 350 UND")
        raw_data = st.text_area("Datos del pedido", height=300)
        if st.button("Reiniciar Simulador"): st.rerun()

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
                        pedido_items.append({
                            "tipo": f"TEJA #{num_ref}", "cant": cant, "peso": cant * info["peso"], 
                            "ref_num": int(num_ref), "largo_ft": info["largo_ft"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        # 1. Selección de Vehículo
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Peso Total Pedido", f"{peso_total_pedido:,.2f} kg")
        with c2: st.metric("Vehículo Asignado", vh['tipo'])
        with c3: 
            utilizacion_peso = (peso_total_pedido / vh['capacidad_max']) * 100
            st.metric("Carga Útil", f"{utilizacion_peso:.1f}%")

        if peso_total_pedido > vh['capacidad_max']:
            st.error(f"⚠️ ATENCIÓN: El peso excede la capacidad de la {vh['tipo']} por {peso_total_pedido - vh['capacidad_max']:,.2f} kg")

        # --- LÓGICA DE DISTRIBUCIÓN (Llenado de Huecos) ---
        # Ordenamos por largo para poner lo más grande adelante (estabilidad)
        pedido_sorted = sorted(pedido_items, key=lambda x: x['largo_ft'], reverse=True)
        
        paquetes_completos = []
        saldos_naranja = []

        for item in pedido_sorted:
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            completos = item["cant"] // paq_max
            sobra = item["cant"] % paq_max
            
            for _ in range(completos):
                paquetes_completos.append({"label": item["tipo"], "cant": paq_max, "largo": item["largo_ft"]})
            
            while sobra > 0:
                unidades = min(sobra, 60)
                saldos_naranja.append({"label": item["tipo"], "cant": unidades, "largo": item["largo_ft"]})
                sobra -= unidades

        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        largo_ocupado = 0
        limite_ft = vh['largo_planchon_ft']
        
        # Procesamos fila por fila hasta agotar material o espacio
        while (paquetes_completos or saldos_naranja) and largo_ocupado < limite_ft:
            cols = st.columns([1, 1.5, 1.5, 1])
            avance_fila = 0
            
            # --- Centro Izquierda ---
            with cols[1]:
                if paquetes_completos:
                    p = paquetes_completos.pop(0)
                    st.markdown(f'<div class="paquete-v">{p["label"]}<br>{p["cant"]} UND</div>', unsafe_allow_html=True)
                    avance_fila = max(avance_fila, p["largo"])
                elif saldos_naranja:
                    s = saldos_naranja.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
                    avance_fila = max(avance_fila, s["largo"])

            # --- Centro Derecha ---
            with cols[2]:
                if paquetes_completos:
                    p = paquetes_completos.pop(0)
                    st.markdown(f'<div class="paquete-v">{p["label"]}<br>{p["cant"]} UND</div>', unsafe_allow_html=True)
                    avance_fila = max(avance_fila, p["largo"])
                elif saldos_naranja:
                    s = saldos_naranja.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
                    avance_fila = max(avance_fila, s["largo"])

            # --- Hueco Lateral Izquierdo ---
            with cols[0]:
                if saldos_naranja:
                    s = saldos_naranja.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
            
            # --- Hueco Lateral Derecho ---
            with cols[3]:
                if saldos_naranja:
                    s = saldos_naranja.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

            largo_ocupado += avance_fila

        # --- Footer de Estado ---
        st.markdown(f'<div style="text-align:right; color:gray;">Espacio utilizado: {largo_ocupado} / {limite_ft} ft</div>', unsafe_allow_html=True)
        
        if paquetes_completos or saldos_naranja:
            st.error(f"🚫 CAPACIDAD DE ESPACIO EXCEDIDA. No se pudo cargar todo el material en los {limite_ft} pies del vehículo.")
        else:
            st.success("✅ DISTRIBUCIÓN OPTIMIZADA: Todo el pedido ha sido ubicado respetando los huecos laterales.")

    else:
        st.warning("👈 Por favor, ingrese los datos del pedido en el panel de la izquierda para generar la simulación.")
