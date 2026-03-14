import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue Eternit", page_icon="🚛", layout="wide")

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

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ==========================================================
# 1. BLOQUE DE INGRESO (LOGIN) - RESTAURADO
# ==========================================================
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        try:
            st.image("logo-eternit-400x150-1.png", use_container_width=True)
        except:
            st.markdown("### ETERNIT - LOGÍSTICA")
        
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
# 2. PANEL DE CARGUE (INTERFAZ ORIGINAL BLINDADA)
# ==========================================================
else:
    # Estilos visuales exactos a tus imágenes
    st.markdown("""
    <style>
    .metric-text { font-size: 48px; font-weight: 400; color: #333; margin-bottom: 0px; }
    .metric-sub { font-size: 24px; color: #666; margin-top: -10px; }
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px; margin: 20px 0; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; font-size:14px; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:10px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #7d6608; font-size:12px; }
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
                ref = match_ref.group(1)
                if ref in PRODUCTOS_BASE:
                    nums = re.findall(r'\d+', line_upper.replace(f"#{ref}", ""))
                    if nums:
                        cant = int(nums[-1])
                        info = PRODUCTOS_BASE[ref]
                        pedido_items.append({
                            "tipo": f"TEJA #{ref}", "cant": cant, "peso": cant * info["peso"], 
                            "ref_num": int(ref), "largo": info["largo_ft"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        # --- MÉTRICAS SUPERIORES ORIGINALES ---
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        m1, m2, m3 = st.columns([1, 1, 1])
        with m1: st.markdown(f'<p class="metric-text">{peso_total_pedido:,.2f} kg</p>', unsafe_allow_html=True)
        with m2: st.markdown(f'<p class="metric-text" style="text-align:center">{vh["tipo"]}</p>', unsafe_allow_html=True)
        with m3: st.markdown(f'<p class="metric-text" style="text-align:right">{vh["largo_planchon_ft"]} ft</p>', unsafe_allow_html=True)
        
        st.divider()

        # --- LÓGICA DE CARGUE INDEPENDIENTE ---
        inventario = []
        for item in sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True):
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            for _ in range(item["cant"] // paq_max):
                inventario.append({"label": item["tipo"], "cant": paq_max, "largo": item["largo"], "es_paq": True})
            sobra = item["cant"] % paq_max
            if sobra > 0:
                inventario.append({"label": item["tipo"], "cant": sobra, "largo": item["largo"], "es_paq": False})

        col_izq, col_der = [], []
        largo_izq, largo_der = 0, 0
        limite = vh['largo_planchon_ft']
        no_cupo = False

        for p in inventario:
            if largo_izq <= largo_der:
                if largo_izq + p['largo'] <= limite:
                    col_izq.append(p); largo_izq += p['largo']
                elif largo_der + p['largo'] <= limite:
                    col_der.append(p); largo_der += p['largo']
                else: no_cupo = True
            else:
                if largo_der + p['largo'] <= limite:
                    col_der.append(p); largo_der += p['largo']
                elif largo_izq + p['largo'] <= limite:
                    col_izq.append(p); largo_izq += p['largo']
                else: no_cupo = True

        # --- DIBUJO DEL VEHÍCULO ---
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        for i in range(max(len(col_izq), len(col_der))):
            c = st.columns([1, 2, 2, 1])
            with c[1]:
                if i < len(col_izq):
                    b = col_izq[i]
                    clase = "paquete-v" if b["es_paq"] else "saldo-box"
                    st.markdown(f'<div class="{clase}">{b["label"]} ({b["cant"]} UND)</div>', unsafe_allow_html=True)
            with c[2]:
                if i < len(col_der):
                    b = col_der[i]
                    clase = "paquete-v" if b["es_paq"] else "saldo-box"
                    st.markdown(f'<div class="{clase}">{b["label"]} ({b["cant"]} UND)</div>', unsafe_allow_html=True)

        # --- ALARMAS ORIGINALES ---
        if peso_total_pedido > 34000:
            st.error(f"⚠️ ALARMA: SE EXCEDE CAPACIDAD POR {peso_total_pedido - 34000:,.2f} KG")
        
        if no_cupo:
            st.warning("⚠️ ALARMA: NO CABE TODO EL PEDIDO EN EL VEHÍCULO POR DIMENSIONES DEL PLANCHÓN.")
