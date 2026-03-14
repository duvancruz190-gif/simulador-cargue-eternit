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

# Límites de peso según tabla proporcionada
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
# INICIO DE SESIÓN (LOGIN CON LOGO RESTAURADO)
# ==========================================================
if not st.session_state.autenticado:
    st.markdown("""
    <style>
    [data-testid="stHeaderActionElements"] {display:none;}
    div.stButton > button {
        background-color:#E30613; color:white; border:none; font-weight:bold; padding:12px; font-size:17px; border-radius:8px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        try:
            # Se asume que el archivo del logo está en la misma carpeta
            st.image("logo-eternit-400x150-1.png", use_container_width=True)
        except:
            st.warning("Logo no encontrado en el servidor")
        
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
# SISTEMA - PANEL PRINCIPAL (DENTRO DEL LOGIN)
# ==========================================================
else:
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - LOGÍSTICA</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; border-bottom:5px solid #bdc3c7; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #7d6608; }
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
                        pedido_items.append({"tipo": f"TEJA #{ref}", "cant": cant, "peso": cant * info["peso"], "ref_num": int(ref), "largo": info["largo_ft"]})
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        # Selección de vehículo y MÉTRICAS
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        # Alarma de Peso
        if peso_total_pedido > 34000:
            st.error(f"❌ EL PEDIDO EXCEDE LA CAPACIDAD MÁXIMA DEL VEHÍCULO POR {peso_total_pedido - 34000:,.2f} KG")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Vehículo Sugerido", vh['tipo'])
        c3.metric("Largo Planchón", f"{vh['largo_planchon_ft']} ft")

        # --- LÓGICA DE CARGUE POR PASOS INDEPENDIENTES ---
        inventario = []
        for item in sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True):
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            # Paquetes Verdes
            for _ in range(item["cant"] // paq_max):
                inventario.append({"label": item["tipo"], "cant": paq_max, "largo": item["largo"], "es_paq": True})
            # Saldos Amarillos
            sobra = item["cant"] % paq_max
            if sobra > 0:
                inventario.append({"label": item["tipo"], "cant": sobra, "largo": item["largo"], "es_paq": False})

        col_izq, col_der = [], []
        largo_izq, largo_der = 0, 0
        limite = vh['largo_planchon_ft']
        fueron_al_planchon = False

        # Asignación a columnas aprovechando huecos
        for p in inventario:
            if largo_izq <= largo_der:
                if largo_izq + p['largo'] <= limite:
                    col_izq.append(p); largo_izq += p['largo']
                elif largo_der + p['largo'] <= limite:
                    col_der.append(p); largo_der += p['largo']
                else: fueron_al_planchon = True
            else:
                if largo_der + p['largo'] <= limite:
                    col_der.append(p); largo_der += p['largo']
                elif largo_izq + p['largo'] <= limite:
                    col_izq.append(p); largo_izq += p['largo']
                else: fueron_al_planchon = True

        # --- DIBUJO ---
        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        for i in range(max(len(col_izq), len(col_der))):
            c = st.columns([1, 2, 2, 1])
            with c[1]:
                if i < len(col_izq):
                    b = col_izq[i]
                    st.markdown(f'<div class="{"paquete-v" if b["es_paq"] else "saldo-box"}">{b["label"]} ({b["cant"]} UND)</div>', unsafe_allow_html=True)
            with c[2]:
                if i < len(col_der):
                    b = col_der[i]
                    st.markdown(f'<div class="{"paquete-v" if b["es_paq"] else "saldo-box"}">{b["label"]} ({b["cant"]} UND)</div>', unsafe_allow_html=True)

        if fueron_al_planchon:
            st.error("⚠️ ALARMA: NO CABE TODO EL PEDIDO EN EL VEHÍCULO POR DIMENSIONES.")
