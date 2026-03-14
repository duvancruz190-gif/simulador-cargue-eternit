import streamlit as st
import pandas as pd
import re
import math

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(
    page_title="Simulador de Cargue Eternit",
    page_icon="🚛",
    layout="wide"
)

USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# BASE PRODUCTOS (Pesos reales y paquete #10 corregido)
PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

# VEHÍCULOS (Ordenados por capacidad y pasos)
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

if not st.session_state.autenticado:
    st.markdown("""
    <style>
    [data-testid="stHeaderActionElements"] {display:none;}
    div.stButton > button { background-color:#E30613; color:white; border:none; font-weight:bold; padding:12px; border-radius:8px; }
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>Simulador de Cargue</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar al Sistema", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    st.stop()

# -----------------------------
# SISTEMA - ESTILOS
# -----------------------------
st.markdown("""
<style>
.cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
.paquete-v { background:#27ae60; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #1e8449; }
.paquete-h { background:#2980b9; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:80%; }
.saldo-card { background:#f1c40f; color:#2c3e50; padding:10px; border-radius:5px; font-weight:bold; margin-bottom:5px; border-left:5px solid #d4ac0d; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.header("📋 Pedido")
    raw_data = st.text_area("Pegue el pedido aquí", height=250, placeholder="TEJA FLEXIFORTE #5 500\nTEJA #10 560")
    if st.button("Limpiar"): st.rerun()

# PROCESAMIENTO
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
                        "tipo": f"TEJA #{num_ref}", "cant": cant, "peso": cant * info["peso"], "ref": num_ref
                    })
                    peso_total_pedido += cant * info["peso"]

# RESULTADOS Y LÓGICA DE PICKING
if pedido_items:
    # 1. Definir referencia líder (la más larga para el cálculo de espacio)
    ref_lider = max(pedido_items, key=lambda x: PRODUCTOS_BASE[x['ref']]['largo_ft'])['ref']
    largo_t = PRODUCTOS_BASE[ref_lider]['largo_ft']
    
    # 2. Buscar Vehículo Óptimo
    total_paq_est = sum(math.ceil(i['cant'] / PRODUCTOS_BASE[i['ref']]['paquete']) for i in pedido_items)
    vh = None
    for v in VEHICULOS:
        cap_lado = v["largo_planchon_ft"] // largo_t
        cap_total = (cap_lado * 2) + (1 if (v["largo_planchon_ft"] % largo_t) >= 4 else 0)
        if peso_total_pedido <= v["capacidad_max"] and total_paq_est <= cap_total:
            vh = v
            break
    if not vh: vh = VEHICULOS[-1]

    # MÉTRICAS
    st.subheader(f"🚛 Vehículo: {vh['tipo']} ({vh['largo_planchon_ft']} ft)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Peso Total", f"{peso_total_pedido:,.1f} kg")
    c2.metric("Capacidad", f"{vh['capacidad_max']} kg")
    c3.metric("Utilización", f"{(peso_total_pedido/vh['capacidad_max']*100):.1f}%")
    c4.metric("Paquetes aprox.", total_paq_est)

    st.divider()

    # 3. Clasificación de Carga (Paquetes Completos vs Saldos)
    lista_paquetes = []
    lista_saldos = []
    for item in pedido_items:
        p_size = PRODUCTOS_BASE[item['ref']]['paquete']
        completos = item["cant"] // p_size
        sobra = item["cant"] % p_size
        for _ in range(completos): lista_paquetes.append({"label": item["tipo"], "cant": p_size})
        if sobra > 0: lista_saldos.append({"label": item["tipo"], "cant": sobra})

    # 4. Distribución en Planchón
    st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
    
    cap_lado_vh = vh["largo_planchon_ft"] // largo_t
    max_planchon = cap_lado_vh * 2
    
    paq_para_filas = lista_paquetes[:max_planchon]
    paq_sobrantes = lista_paquetes[max_planchon:]
    
    rows = [paq_para_filas[i:i+2] for i in range(0, len(paq_para_filas), 2)]
    for row in rows:
        cols = st.columns([1, 1.5, 1.5, 1])
        with cols[1]: st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
        with cols[2]:
            if len(row) > 1: st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)

    # Paquete Atravesado
    sobrante_ft = vh["largo_planchon_ft"] % largo_t
    if sobrante_ft >= 4 and paq_sobrantes:
        atravesado = paq_sobrantes.pop(0)
        st.markdown(f'<div class="paquete-h">📦 ATRAVESADO EN COLA ({sobrante_ft}ft)<br>{atravesado["label"]} ({atravesado["cant"]} UND)</div>', unsafe_allow_html=True)

    # 5. SALDOS Y CARGA ENCIMA
    st.divider()
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.markdown("### ⚠️ Saldos (Tejas Sueltas)")
        if lista_saldos:
            for s in lista_saldos:
                st.markdown(f'<div class="saldo-card">{s["label"]}: {s["cant"]} UNIDADES</div>', unsafe_allow_html=True)
        else: st.write("No hay saldos sueltos.")
    
    with col_inf2:
        st.markdown("### 📦 Carga Superior (Encima)")
        if paq_sobrantes:
            for p in paq_sobrantes:
                st.info(f"Cargar arriba: {p['label']} ({p['cant']} UND)")
        else: st.write("Toda la carga cabe en el planchón base.")

else:
    st.info("Pegue el pedido para iniciar la simulación.")
