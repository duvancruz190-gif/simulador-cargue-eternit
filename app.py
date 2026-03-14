import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------

st.set_page_config(
    page_title="Simulador de Cargue",
    page_icon="🚛",
    layout="wide"
)

USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# -----------------------------
# BASE PRODUCTOS
# -----------------------------

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

# -----------------------------
# VEHÍCULOS
# -----------------------------

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

# -----------------------------
# ESTADO LOGIN
# -----------------------------

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ==========================================================
# LOGIN (RESTABLECIDO AL ORIGINAL)
# ==========================================================

if not st.session_state.autenticado:

    st.markdown("""
    <style>
    [data-testid="stHeaderActionElements"] {display:none;}
    div.stButton > button {
        background-color:#E30613;
        color:white;
        border:none;
        font-weight:bold;
        padding:12px;
        font-size:17px;
        border-radius:8px;
    }
    div.stButton > button:hover{
        background-color:#b3050f;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1.4,1])

    with col2:
        # st.image("logo-eternit-400x150-1.png", use_container_width=True)

        st.markdown(
        """
        <h1 style='text-align:center;
        color:#1A3A5A;
        font-weight:800;
        font-size:40px;
        margin-top:10px'>
        Simulador de Cargue
        </h1>
        """,
        unsafe_allow_html=True
        )

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
# SISTEMA (CON LÓGICA DE LÍMITES POR PASOS)
# ==========================================================

else:

    st.markdown("""
    <div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">
    🚛 SIMULADOR DE CARGUE - LOGÍSTICA
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; border-bottom:5px solid #bdc3c7; }
    .paquete-v { background:#27ae60; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #1e8449; }
    .paquete-h { background:#2980b9; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:80%; }
    .saldo-box { background:#f1c40f; color:#2c3e50; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #d4ac0d; }
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
                        pedido_items.append({"tipo": f"FLEX. #{num_ref}", "cant": cant, "peso": cant * info["peso"], "ref": num_ref})
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        # MOSTRAR MÉTRICAS (SOLO AQUÍ SE AGREGÓ EL PORCENTAJE)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Peso Total", f"{peso_total_pedido:,.0f} kg")
        c2.metric("Capacidad Máx", f"{vh['capacidad_max']:,.0f} kg")
        c3.metric("Ocupación %", f"{(peso_total_pedido/vh['capacidad_max']):.1%}")
        c4.metric("Largo Libre", f"{vh['largo_planchon_ft']} ft")

        st.divider()

        # LÓGICA DE DISTRIBUCIÓN POR LARGOS (PASOS)
        pedido_sorted = sorted(pedido_items, key=lambda x: PRODUCTOS_BASE[x['ref']]['largo_ft'], reverse=True)
        paquetes_lista = []
        saldos = []

        for item in pedido_sorted:
            paq_std = PRODUCTOS_BASE[item['ref']]['paquete']
            completos = item["cant"] // paq_std
            sobra = item["cant"] % paq_std
            for _ in range(completos):
                paquetes_lista.append({"label": item["tipo"], "cant": paq_std, "ref": item["ref"]})
            while sobra > 0:
                cant_s = min(sobra, 60)
                saldos.append({"label": item["tipo"], "cant": cant_s})
                sobra -= cant_s

        # Cálculo de largo ocupado real
        tiene_atravesado = len(paquetes_lista) % 2 != 0
        paquetes_pares = paquetes_lista[:-1] if tiene_atravesado else paquetes_lista
        paquete_final = paquetes_lista[-1] if tiene_atravesado else None

        largo_usado = 0
        for i in range(0, len(paquetes_pares), 2):
            largo_usado += PRODUCTOS_BASE[paquetes_pares[i]['ref']]['largo_ft']
        if tiene_atravesado:
            # Si es #4, #5, #6 o #8 atravesado ocupa 4 pasos (pies)
            largo_usado += (4 if paquete_final['ref'] != "10" else PRODUCTOS_BASE[paquete_final['ref']]['largo_ft'])

        # EL FRENO: Si supera el largo del vehículo, no dibuja y avisa
        if largo_usado > vh["largo_planchon_ft"]:
            st.error(f"❌ ¡EL MATERIAL NO CABE! Se requieren {largo_usado} pies (pasos) y el vehículo solo tiene {vh['largo_planchon_ft']}.")
        else:
            st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
            
            rows_verdes = [paquetes_pares[i:i+2] for i in range(0, len(paquetes_pares), 2)]
            saldos_render = list(saldos)
            max_filas = max(len(rows_verdes), (len(saldos_render) + 1) // 2)

            for i in range(max_filas):
                cols = st.columns([1,1.5,1.5,1])
                with cols[0]:
                    if saldos_render:
                        s = saldos_render.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
                if i < len(rows_verdes):
                    row = rows_verdes[i]
                    with cols[1]: st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
                    with cols[2]: 
                        if len(row) > 1: st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)
                with cols[3]:
                    if saldos_render:
                        s = saldos_render.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

            if tiene_atravesado:
                st.markdown(f'<div class="paquete-h">📦 PAQUETE ATRAVESADO (4 PASOS)<br>{paquete_final["label"]} ({paquete_final["cant"]} UND)</div>', unsafe_allow_html=True)
            
            st.success(f"Cargue validado: {largo_usado} pasos ocupados de {vh['largo_planchon_ft']} disponibles.")

    else:
        st.info("Pegue un pedido para simular.")
