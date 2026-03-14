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

# Límites de peso actualizados según tu tabla
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
    # --- INTERFAZ DE CARGUE ---
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - EQUILIBRIO DE PESOS</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px; margin-bottom:10px; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:10px; margin:2px; border-radius:4px; font-weight:bold; border:1px solid #0d3b11; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:10px; margin:2px; border-radius:4px; font-weight:bold; border:1px solid #7d6608; }
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
        # Selección de vehículo y Alarmas de Peso
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        if peso_total_pedido > 34000:
            st.error(f"❌ ALERTA: Peso excedido ({peso_total_pedido:,.0f} kg). Máximo permitido 34,000 kg.")
        
        st.subheader(f"Vehículo: {vh['tipo']} | Largo: {vh['largo_planchon_ft']} ft")

        # --- DISTRIBUCIÓN SIMÉTRICA ---
        inventario = []
        # Ordenamos de mayor a menor para que la base sea estable
        for item in sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True):
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            for _ in range(item["cant"] // paq_max):
                inventario.append({"label": item["tipo"], "cant": paq_max, "largo": item["largo"], "es_paq": True})
            sobra = item["cant"] % paq_max
            if sobra > 0:
                # Si el saldo es grande, lo partimos para equilibrar peso a los lados
                if sobra > 40:
                    inventario.append({"label": item["tipo"], "cant": sobra//2, "largo": item["largo"], "es_paq": False})
                    inventario.append({"label": item["tipo"], "cant": sobra - (sobra//2), "largo": item["largo"], "es_paq": False})
                else:
                    inventario.append({"label": item["tipo"], "cant": sobra, "largo": item["largo"], "es_paq": False})

        col_izq, col_der = [], []
        largo_izq, largo_der = 0, 0
        limite = vh['largo_planchon_ft']
        fueron_al_planchon = []

        # Llenado por parejas primero para forzar equilibrio de peso
        i = 0
        while i < len(inventario):
            p1 = inventario[i]
            # Si hay un par igual, los mandamos uno a cada lado
            if i + 1 < len(inventario) and inventario[i+1]['label'] == p1['label']:
                p2 = inventario[i+1]
                if largo_izq + p1['largo'] <= limite and largo_der + p2['largo'] <= limite:
                    col_izq.append(p1); largo_izq += p1['largo']
                    col_der.append(p2); largo_der += p2['largo']
                i += 2
            else:
                # Si está solo, lo mandamos al lado con más espacio
                if largo_izq <= largo_der:
                    if largo_izq + p1['largo'] <= limite:
                        col_izq.append(p1); largo_izq += p1['largo']
                    else: fueron_al_planchon.append(p1)
                else:
                    if largo_der + p1['largo'] <= limite:
                        col_der.append(p1); largo_der += p1['largo']
                    else: fueron_al_planchon.append(p1)
                i += 1

        # DIBUJO
        st.markdown('<div class="cabina">CABINA DEL VEHÍCULO</div>', unsafe_allow_html=True)
        for row_idx in range(max(len(col_izq), len(col_der))):
            c = st.columns([1, 2, 2, 1])
            with c[1]:
                if row_idx < len(col_izq):
                    b = col_izq[row_idx]
                    st.markdown(f'<div class="{"paquete-v" if b["es_paq"] else "saldo-box"}">{b["label"]}<br>({b["cant"]} UND)</div>', unsafe_allow_html=True)
            with c[2]:
                if row_idx < len(col_der):
                    b = col_der[row_idx]
                    st.markdown(f'<div class="{"paquete-v" if b["es_paq"] else "saldo-box"}">{b["label"]}<br>({b["cant"]} UND)</div>', unsafe_allow_html=True)

        if fueron_al_planchon or (largo_izq > limite or largo_der > limite):
            st.error("⚠️ ALARMA: NO CABE TODO EL PEDIDO EN EL PLANCHÓN.")
