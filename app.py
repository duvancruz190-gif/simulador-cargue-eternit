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
# LOGIN
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
        try:
            st.image("logo-eternit-400x150-1.png", use_container_width=True)
        except:
            st.error("Logo no encontrado")
        st.markdown("<h1 style='text-align:center; color:#1A3A5A; font-weight:800; font-size:40px; margin-top:10px'>Simulador de Cargue</h1>", unsafe_allow_html=True)
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
# SISTEMA - PANEL PRINCIPAL
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
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; }
    .paquete-h { background:#1b4f72; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:80%; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #7d6608; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Pedido")
        raw_data = st.text_area("Pegue el pedido aquí", height=300, placeholder="Ejemplo:\nTEJA FLEXIFORTE #5 900")
        if st.button("Limpiar"):
            st.rerun()

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
                        nombre = f"FLEX. #{num_ref}" if "FLEXIFORTE" in line_upper else f"TEJA #{num_ref}"
                        pedido_items.append({
                            "tipo": nombre, "cant": cant, "peso": cant * info["peso"], "ref": num_ref, "largo_ft": info["largo_ft"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        st.subheader(f"🚛 Vehículo sugerido: {vh['tipo']}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Capacidad Vehículo", f"{vh['capacidad_max']:,.0f} kg")
        c3.metric("Largo Planchón", f"{vh['largo_planchon_ft']} ft")
        
        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        # --- LÓGICA DE DISTRIBUCIÓN MEJORADA ---
        pedido_sorted = sorted(pedido_items, key=lambda x: x['largo_ft'], reverse=True)

        mapa_paquetes = []
        saldos_lista = []

        for item in pedido_sorted:
            paq_config = PRODUCTOS_BASE[item['ref']]['paquete']
            completos = item["cant"] // paq_config
            sobra = item["cant"] % paq_config

            for _ in range(completos):
                mapa_paquetes.append({"label": item["tipo"], "cant": paq_config, "largo": item["largo_ft"]})

            # LÓGICA DE EQUILIBRIO DE SALDOS:
            # Si el saldo es significativo (ej. > 10), lo dividimos en dos bloques para repartir peso
            if sobra > 10:
                mitad1 = sobra // 2
                mitad2 = sobra - mitad1
                saldos_lista.append({"label": item["tipo"], "cant": mitad1, "largo": item["largo_ft"]})
                saldos_lista.append({"label": item["tipo"], "cant": mitad2, "largo": item["largo_ft"]})
            elif sobra > 0:
                saldos_lista.append({"label": item["tipo"], "cant": sobra, "largo": item["largo_ft"]})

        paq_render = list(mapa_paquetes)
        atravesado = paq_render.pop() if len(paq_render) % 2 != 0 else None
        rows = [paq_render[i:i+2] for i in range(0, len(paq_render), 2)]
        saldos_render = list(saldos_lista)

        # --- RENDERIZADO ---
        largo_ocupado = 0
        limite_ft = vh['largo_planchon_ft']

        for row in rows:
            avance_fila = max([p['largo'] for p in row])
            if largo_ocupado + avance_fila <= limite_ft:
                cols = st.columns([1, 1.5, 1.5, 1])
                
                with cols[0]: # Saldo Izquierda
                    if saldos_render:
                        s = saldos_render.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
                
                with cols[1]: # Paquete 1
                    st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
                
                with cols[2]: # Paquete 2
                    if len(row) > 1:
                        st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)
                
                with cols[3]: # Saldo Derecha
                    if saldos_render:
                        s = saldos_render.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
                
                largo_ocupado += avance_fila
            else:
                st.warning(f"⚠️ Se alcanzó el límite de {limite_ft} ft.")
                break

        if atravesado:
            if largo_ocupado + atravesado['largo'] <= limite_ft:
                # Al final, si quedan saldos por mostrar, los ponemos a los lados del atravesado
                cols_final = st.columns([1, 3, 1])
                with cols_final[0]:
                    if saldos_render:
                        s = saldos_render.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
                with cols_final[1]:
                    st.markdown(f'<div class="paquete-h">📦 PAQUETE TRASERO<br>{atravesado["label"]} ({atravesado["cant"]} UND)</div>', unsafe_allow_html=True)
                with cols_final[2]:
                    if saldos_render:
                        s = saldos_render.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
