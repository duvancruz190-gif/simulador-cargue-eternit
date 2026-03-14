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
        try: st.image("logo-eternit-400x150-1.png", use_container_width=True)
        except: st.warning("Logo no encontrado")
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
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; font-size:13px; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:12px; font-weight:800; border:1px solid #7d6608; }
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
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        limite_ft = vh['largo_planchon_ft']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Vehículo Sugerido", vh['tipo'])
        c3.metric("Largo Máximo", f"{limite_ft} ft")

        # --- LÓGICA DE DISTRIBUCIÓN BASADA EN ESQUEMA ---
        pedido_sorted = sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True)
        paquetes_verdes = []
        saldos_naranja = []

        for item in pedido_sorted:
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            completos = item["cant"] // paq_max
            sobra = item["cant"] % paq_max
            for _ in range(completos):
                paquetes_verdes.append({"label": item["tipo"], "cant": paq_max, "largo": item["largo_ft"]})
            # Los saldos se agrupan en lotes de hasta 60 como en tu Excel
            while sobra > 0:
                unidades = min(sobra, 60)
                saldos_naranja.append({"label": item["tipo"], "cant": unidades, "largo": item["largo_ft"]})
                sobra -= unidades

        # Repartir en 4 carriles (Lateral Izq, Centro 1, Centro 2, Lateral Der)
        col_izq, col_c1, col_c2, col_der = [], [], [], []
        
        # Centro: Paquetes Verdes
        for i, p in enumerate(paquetes_verdes):
            if i % 2 == 0: col_c1.append(p)
            else: col_c2.append(p)
            
        # Laterales: Saldos (distribución balanceada)
        for i, s in enumerate(saldos_naranja):
            if i % 2 == 0: col_izq.append(s)
            else: col_der.append(s)

        st.divider()
        st.markdown('<div class="cabina">CABINA</div>', unsafe_allow_html=True)

        # Renderizado de filas dinámicas
        max_rows = max(len(col_izq), len(col_c1), len(col_c2), len(col_der))
        for i in range(max_rows):
            cols = st.columns([1, 1, 1, 1])
            with cols[0]:
                if i < len(col_izq):
                    st.markdown(f'<div class="saldo-box">{col_izq[i]["label"]} SALDO {col_izq[i]["cant"]}</div>', unsafe_allow_html=True)
            with cols[1]:
                if i < len(col_c1):
                    st.markdown(f'<div class="paquete-v">{col_c1[i]["label"]}: {col_c1[i]["cant"]} UND</div>', unsafe_allow_html=True)
            with cols[2]:
                if i < len(col_c2):
                    st.markdown(f'<div class="paquete-v">{col_c2[i]["label"]}: {col_c2[i]["cant"]} UND</div>', unsafe_allow_html=True)
            with cols[3]:
                if i < len(col_der):
                    st.markdown(f'<div class="saldo-box">{col_der[i]["label"]} SALDO {col_der[i]["cant"]}</div>', unsafe_allow_html=True)

        # Cálculo de "Pasos" (Longitud por carril)
        pasos_izq = sum(x['largo'] for x in col_izq)
        pasos_c1 = sum(x['largo'] for x in col_c1)
        pasos_c2 = sum(x['largo'] for x in col_c2)
        pasos_der = sum(x['largo'] for x in col_der)
        
        max_pasos = max(pasos_izq, pasos_c1, pasos_c2, pasos_der)

        st.markdown("---")
        st.subheader("📊 Resumen de Espacio (Pies)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Lateral Izquierdo", f"{pasos_izq} ft")
        m2.metric("Centro (Máximo)", f"{max(pasos_c1, pasos_c2)} ft")
        m3.metric("Lateral Derecho", f"{pasos_der} ft")

        if max_pasos <= limite_ft:
            st.success(f"✅ ¡CARGUE EXITOSO! El pedido completo cabe en {max_pasos} ft.")
        else:
            st.error(f"⚠️ EL CARGUE EXCEDE EL LARGO: {max_pasos} ft ocupados.")
