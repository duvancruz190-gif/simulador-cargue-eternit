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
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; font-size:14px; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:12px; font-weight:800; border:1px solid #7d6608; }
    .metric-box { background:#f8f9fa; padding:10px; border-radius:8px; border-left: 5px solid #E30613; }
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
        c2.metric("Vehículo", vh['tipo'])
        c3.metric("Largo Disponible", f"{limite_ft} ft")

        # --- LÓGICA DE DISTRIBUCIÓN TIPO EXCEL ---
        pedido_sorted = sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True)
        paquetes_verdes = []
        saldos_naranja = []

        for item in pedido_sorted:
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            completos = item["cant"] // paq_max
            sobra = item["cant"] % paq_max
            for _ in range(completos):
                paquetes_verdes.append({"label": item["tipo"], "cant": paq_max, "largo": item["largo_ft"]})
            if sobra > 0:
                saldos_naranja.append({"label": item["tipo"], "cant": sobra, "largo": item["largo_ft"]})

        # Preparamos las columnas como en tu esquema
        col_izq = []
        col_centro_1 = []
        col_centro_2 = []
        col_der = []

        # Llenamos el centro (Paquetes Verdes)
        temp_verdes = list(paquetes_verdes)
        while temp_verdes:
            col_centro_1.append(temp_verdes.pop(0))
            if temp_verdes:
                col_centro_2.append(temp_verdes.pop(0))

        # Llenamos los laterales con saldos (Reparto balanceado)
        temp_saldos = list(saldos_naranja)
        while temp_saldos:
            col_izq.append(temp_saldos.pop(0))
            if temp_saldos:
                col_der.append(temp_saldos.pop(0))

        st.divider()
        st.markdown('<div class="cabina">CABINA</div>', unsafe_allow_html=True)

        # Determinar cuántas filas visuales necesitamos
        max_rows = max(len(col_izq), len(col_centro_1), len(col_centro_2), len(col_der))

        # RENDERIZADO DE LA GRILLA
        for i in range(max_rows):
            c = st.columns([1, 1, 1, 1])
            
            with c[0]: # Lateral Izquierdo
                if i < len(col_izq):
                    s = col_izq[i]
                    st.markdown(f'<div class="saldo-box">{s["label"]} SALDO {s["cant"]}</div>', unsafe_allow_html=True)
            
            with c[1]: # Centro 1
                if i < len(col_centro_1):
                    p = col_centro_1[i]
                    st.markdown(f'<div class="paquete-v">{p["label"]}: {p["cant"]} UND</div>', unsafe_allow_html=True)
            
            with c[2]: # Centro 2
                if i < len(col_centro_2):
                    p = col_centro_2[i]
                    st.markdown(f'<div class="paquete-v">{p["label"]}: {p["cant"]} UND</div>', unsafe_allow_html=True)
            
            with c[3]: # Lateral Derecho
                if i < len(col_der):
                    s = col_der[i]
                    st.markdown(f'<div class="saldo-box">{s["label"]} SALDO {s["cant"]}</div>', unsafe_allow_html=True)

        # CÁLCULO DE PASOS (PIES) REALES
        pasos_izq = sum(x['largo'] for x in col_izq)
        pasos_centro = sum(x['largo'] for x in col_centro_1)
        pasos_der = sum(x['largo'] for x in col_der)
        
        largo_maximo_final = max(pasos_izq, pasos_centro, pasos_der)

        st.markdown("---")
        if largo_maximo_final <= limite_ft:
            st.success(f"✅ CARGUE COMPLETADO - LARGO OCUPADO: {largo_maximo_final} ft / {limite_ft} ft")
        else:
            st.error(f"⚠️ EL CARGUE EXCEDE EL LARGO: {largo_maximo_final} ft ocupados.")
