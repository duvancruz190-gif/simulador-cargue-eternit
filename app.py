import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue Pro", page_icon="🚛", layout="wide")

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
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - LÓGICA POR CARRILES</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; height: 100px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #7d6608; }
    .indicador-pies { color: #555; font-size: 12px; font-style: italic; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Pedido")
        raw_data = st.text_area("Pegue el pedido aquí (Ej: TEJA #10 560)", height=300)
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
        # Selección de vehículo
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Vehículo Sugerido", vh['tipo'])
        c3.metric("Largo Disponible", f"{vh['largo_planchon_ft']} ft")

        if peso_total_pedido > VEHICULOS[-1]['capacidad_max']:
            st.error(f"❌ EXCESO DE PESO: {peso_total_pedido - VEHICULOS[-1]['capacidad_max']:,.2f} KG")

        # --- NUEVA LÓGICA DE DISTRIBUCIÓN POR CARRILES ---
        pedido_sorted = sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True)
        
        todos_los_paquetes = []
        saldos = []

        for item in pedido_sorted:
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            completos = item["cant"] // paq_max
            sobra = item["cant"] % paq_max
            for _ in range(completos):
                todos_los_paquetes.append({"label": item["tipo"], "cant": paq_max, "largo": item["largo_ft"]})
            if sobra > 0:
                saldos.append({"label": item["tipo"], "cant": sobra, "largo": item["largo_ft"]})

        # Dividir paquetes en dos carriles
        carril_izq = []
        carril_der = []
        largo_izq = 0
        largo_der = 0

        for p in todos_los_paquetes:
            if largo_izq <= largo_der:
                carril_izq.append(p)
                largo_izq += p['largo']
            else:
                carril_der.append(p)
                largo_der += p['largo']

        # --- RENDERIZADO ---
        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        col_izq_ext, col_izq_int, col_der_int, col_der_ext = st.columns([1, 2, 2, 1])

        # Carril Izquierdo
        with col_izq_int:
            for p in carril_izq:
                st.markdown(f'<div class="paquete-v">{p["label"]}<br>({p["cant"]} UND)<br><small>{p["largo"]} ft</small></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="indicador-pies">Total Izq: {largo_izq} ft</div>', unsafe_allow_html=True)

        # Carril Derecho
        with col_der_int:
            for p in carril_der:
                st.markdown(f'<div class="paquete-v">{p["label"]}<br>({p["cant"]} UND)<br><small>{p["largo"]} ft</small></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="indicador-pies">Total Der: {largo_der} ft</div>', unsafe_allow_html=True)

        # Saldos en los laterales
        with col_izq_ext:
            for i, s in enumerate(saldos):
                if i % 2 == 0: st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
        with col_der_ext:
            for i, s in enumerate(saldos):
                if i % 2 != 0: st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        # Verificación de espacio
        if largo_izq > vh['largo_planchon_ft'] or largo_der > vh['largo_planchon_ft']:
            st.error(f"⚠️ ¡ATENCIÓN! La carga supera los {vh['largo_planchon_ft']} ft del vehículo.")
        else:
            st.success(f"✅ Cargue optimizado. Espacio máximo ocupado: {max(largo_izq, largo_der)} ft.")
