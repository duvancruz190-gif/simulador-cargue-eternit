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

# Límites según tu tabla de referencia
VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- LOGIN (SIN CAMBIOS) ---
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        with st.container(border=True):
            st.title("Acceso")
            usuario = st.text_input("Usuario").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("INGRESAR", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Acceso denegado")
else:
    # --- INTERFAZ PRINCIPAL ---
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - ETERNIT</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px; margin-bottom:10px; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:10px; margin:2px; border-radius:4px; font-weight:bold; border:1px solid #0d3b11; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:10px; margin:2px; border-radius:4px; font-weight:bold; border:1px solid #7d6608; }
    .paquete-h { background:#1b4f72; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:80%; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Pedido")
        raw_data = st.text_area("Pegue el pedido aquí", height=250)
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
        # Selección de vehículo y MÉTRICAS (Restauradas)
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        # Alarma de Peso
        if peso_total_pedido > 34000:
            st.error(f"❌ EL PEDIDO EXCEDE LA CAPACIDAD MÁXIMA DEL VEHÍCULO POR {peso_total_pedido - 34000:,.2f} KG")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Vehículo Sugerido", vh['tipo'])
        c3.metric("Largo Planchón", f"{vh['largo_planchon_ft']} ft")

        # --- LÓGICA DE CARGUE POR PASOS ---
        inventario = []
        for item in sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True):
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            for _ in range(item["cant"] // paq_max):
                inventario.append({"label": item["tipo"], "cant": paq_max, "largo": item["largo"], "es_paq": True, "ref": item["ref_num"]})
            sobra = item["cant"] % paq_max
            if sobra > 0:
                inventario.append({"label": item["tipo"], "cant": sobra, "largo": item["largo"], "es_paq": False, "ref": item["ref_num"]})

        col_izq, col_der = [], []
        largo_izq, largo_der = 0, 0
        limite = vh['largo_planchon_ft']
        atrasado = None
        no_cabe_nada_mas = False

        # Asignación por columnas para aprovechar espacios
        for p in inventario:
            if largo_izq <= largo_der:
                if largo_izq + p['largo'] <= limite:
                    col_izq.append(p); largo_izq += p['largo']
                else: no_cabe_nada_mas = True
            else:
                if largo_der + p['largo'] <= limite:
                    col_der.append(p); largo_der += p['largo']
                else: no_cabe_nada_mas = True

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

        # Alarma de espacio
        if no_cabe_nada_mas:
            st.error("⚠️ NO CABE TODO EL PEDIDO POR DIMENSIONES FÍSICAS DEL PLANCHÓN.")
