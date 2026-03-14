import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue Profesional", page_icon="🚛", layout="wide")

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
# LOGIN (SIN CAMBIOS)
# ==========================================================
if not st.session_state.autenticado:
    st.markdown("""<style>[data-testid="stHeaderActionElements"] {display:none;} div.stButton > button {background-color:#E30613; color:white; border:none; font-weight:bold; padding:12px; font-size:17px; border-radius:8px;} div.stButton > button:hover{background-color:#b3050f;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        st.markdown("<h1 style='text-align:center; color:#1A3A5A; font-weight:800; font-size:40px; margin-top:10px'>Simulador de Cargue</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar al Sistema", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Credenciales incorrectas")

# ==========================================================
# SISTEMA - LÓGICA DE ESTIBA PROFESIONAL
# ==========================================================
else:
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE TÉCNICO (MULAS COLOMBIA)</div>', unsafe_allow_html=True)
    st.markdown("""<style>.cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; border-bottom:5px solid #bdc3c7; } .paquete-v { background:#27ae60; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #1e8449; min-height:90px; } .paquete-h { background:#2980b9; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:80%; } .saldo-box { background:#f1c40f; color:#2c3e50; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #d4ac0d; min-height:70px; }</style>""", unsafe_allow_html=True)

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
                        pedido_items.append({"tipo": f"FLEX. #{num_ref}", "cant": cant, "peso": cant * info["peso"], "ref": num_ref, "largo": info["largo_ft"]})
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        # 1. Definir Vehículo
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        st.subheader(f"Vehículo: {vh['tipo']}")

        # 2. Separar Paquetes Verdes (Base) y Amarillos (Saldos)
        # IMPORTANTE: Ordenar por largo descendente para que lo más largo vaya en la base/adelante
        pedido_sorted = sorted(pedido_items, key=lambda x: x['largo'], reverse=True)
        paquetes_base = []
        saldos_lista = []

        for item in pedido_sorted:
            paq_std = PRODUCTOS_BASE[item['ref']]['paquete']
            completos = item["cant"] // paq_std
            sobra = item["cant"] % paq_std
            for _ in range(completos):
                paquetes_base.append({"label": item["tipo"], "cant": paq_std, "largo": item["largo"]})
            while sobra > 0:
                cant_s = min(sobra, 60)
                saldos_lista.append({"label": item["tipo"], "cant": cant_s, "largo": item["largo"]})
                sobra -= cant_s

        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        # 3. Lógica de Estiba por Filas
        atravesado = len(paquetes_base) % 2 != 0
        verdes_pares = paquetes_base[:-1] if atravesado else paquetes_base
        paq_final_h = paquetes_base[-1] if atravesado else None

        rows_base = [verdes_pares[i:i+2] for i in range(0, len(verdes_pares), 2)]
        saldos_piso = []
        
        for fila in rows_base:
            cols = st.columns([1, 1.5, 1.5, 1])
            
            # --- Lado Izquierdo ---
            with cols[1]: # BASE VERDE IZQ
                st.markdown(f'<div class="paquete-v">📦 BASE<br>{fila[0]["label"]}<br>({fila[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[0]: # SALDO ARRIBA IZQ
                # REGLA: Solo sube si el saldo es <= largo que la base
                if saldos_lista and saldos_lista[0]["largo"] <= fila[0]["largo"]:
                    s = saldos_lista.pop(0)
                    st.markdown(f'<div class="saldo-box">⬆️ ARRIBA<br>{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
            
            # --- Lado Derecho ---
            with cols[2]: # BASE VERDE DER
                if len(fila) > 1:
                    st.markdown(f'<div class="paquete-v">📦 BASE<br>{fila[1]["label"]}<br>({fila[1]["cant"]})</div>', unsafe_allow_html=True)
            with cols[3]: # SALDO ARRIBA DER
                if len(fila) > 1 and saldos_lista and saldos_lista[0]["largo"] <= fila[1]["largo"]:
                    s = saldos_lista.pop(0)
                    st.markdown(f'<div class="saldo-box">⬆️ ARRIBA<br>{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        # 4. Paquete Atravesado (Base Final)
        if paq_final_h:
            st.markdown(f'<div class="paquete-h">🚛 BASE TRASERA<br>{paq_final_h["label"]} ({paq_final_h["cant"]} UND)</div>', unsafe_allow_html=True)

        # 5. Todo lo que NO cupo arriba por ser muy largo o por falta de espacio, VA AL PISO
        saldos_restantes = saldos_lista
        if saldos_restantes:
            st.divider()
            st.subheader("📍 Mercancía en el Piso (Cola del Vehículo)")
            cols_piso = st.columns(4)
            for i, s in enumerate(saldos_restantes):
                with cols_piso[i % 4]:
                    st.markdown(f'<div class="saldo-box">📍 PISO<br>{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
    else:
        st.info("Pegue el pedido para validar la estiba técnica.")
