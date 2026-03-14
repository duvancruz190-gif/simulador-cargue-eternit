import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue Real", page_icon="🚛", layout="wide")

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
# SISTEMA - CARGUE OPERATIVO REAL
# ==========================================================
else:
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 OPERACIÓN DE CARGUE REAL</div>', unsafe_allow_html=True)
    st.markdown("""<style>.cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; border-bottom:5px solid #bdc3c7; } .paquete-v { background:#27ae60; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #1e8449; min-height:80px; display:flex; align-items:center; justify-content:center; } .paquete-h { background:#2980b9; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:80%; } .saldo-box { background:#f1c40f; color:#2c3e50; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #d4ac0d; min-height:60px; }</style>""", unsafe_allow_html=True)

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
                        pedido_items.append({"tipo": f"FLEX. #{num_ref}", "cant": cant, "peso": cant * info["peso"], "ref": num_ref})
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        # Dashboard de capacidad
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Peso Total", f"{peso_total_pedido:,.0f} kg")
        c2.metric("Capacidad Máx", f"{vh['capacidad_max']:,.0f} kg")
        c3.metric("Ocupación %", f"{(peso_total_pedido/vh['capacidad_max']):.1%}")
        c4.metric("Planchón", f"{vh['largo_planchon_ft']} ft")
        st.progress(min(peso_total_pedido/vh['capacidad_max'], 1.0))

        # Clasificación de bultos
        pedido_sorted = sorted(pedido_items, key=lambda x: PRODUCTOS_BASE[x['ref']]['largo_ft'], reverse=True)
        paquetes_base = []
        saldos_menudeo = []

        for item in pedido_sorted:
            paq_std = PRODUCTOS_BASE[item['ref']]['paquete']
            completos = item["cant"] // paq_std
            sobra = item["cant"] % paq_std
            for _ in range(completos):
                paquetes_base.append({"label": item["tipo"], "cant": paq_std})
            while sobra > 0:
                cant_s = min(sobra, 60)
                saldos_menudeo.append({"label": item["tipo"], "cant": cant_s})
                sobra -= cant_s

        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        # Lógica de estiba: Primero se llenan las parejas de base
        atravesado = len(paquetes_base) % 2 != 0
        verdes_pares = paquetes_base[:-1] if atravesado else paquetes_base
        paq_final_h = paquetes_base[-1] if atravesado else None

        rows_base = [verdes_pares[i:i+2] for i in range(0, len(verdes_pares), 2)]
        saldos_cola = list(saldos_menudeo)

        # Render de filas con base sólida
        for fila in rows_base:
            cols = st.columns([1, 1.5, 1.5, 1])
            with cols[0]: # Lateral Izquierdo (Saldos)
                if saldos_cola:
                    s = saldos_cola.pop(0)
                    st.markdown(f'<div class="saldo-box">📦 SALDO<br>{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
            with cols[1]: # Base Verde Izq
                st.markdown(f'<div class="paquete-v">🚛 BASE<br>{fila[0]["label"]}<br>({fila[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]: # Base Verde Der
                if len(fila) > 1:
                    st.markdown(f'<div class="paquete-v">🚛 BASE<br>{fila[1]["label"]}<br>({fila[1]["cant"]})</div>', unsafe_allow_html=True)
            with cols[3]: # Lateral Derecho (Saldos)
                if saldos_cola:
                    s = saldos_cola.pop(0)
                    st.markdown(f'<div class="saldo-box">📦 SALDO<br>{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        # Paquete atravesado (si existe) cierra la base
        if paq_final_h:
            st.markdown(f'<div class="paquete-h">🚛 BASE FINAL (ATRAVESADO)<br>{paq_final_h["label"]} ({paq_final_h["cant"]} UND)</div>', unsafe_allow_html=True)

        # Saldos restantes van a la cola (piso del planchón)
        if saldos_cola:
            st.write("---")
            st.caption("Saldos adicionales al final del planchón:")
            while saldos_cola:
                c_menudeo = st.columns(4)
                for i in range(4):
                    if saldos_cola:
                        s = saldos_cola.pop(0)
                        with c_menudeo[i]:
                            st.markdown(f'<div class="saldo-box">📍 PISO<br>{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
    else:
        st.info("Ingrese un pedido real para calcular la estiba.")
