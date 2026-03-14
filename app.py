import streamlit as st
import pandas as pd
import re

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

# -----------------------------
# BASE PRODUCTOS Y COLORES
# -----------------------------
# Asignamos un color vibrante a cada medida
PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4, "color": "#FF5733"}, # Naranja
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5, "color": "#33FF57"}, # Verde
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6, "color": "#33C1FF"}, # Celeste
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8, "color": "#F333FF"}, # Morado
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10, "color": "#FFBD33"}, # Amarillo
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
# LOGIN (Se mantiene igual, optimizado)
# ==========================================================
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#E30613;'>🔴 ETERNIT</h1>", unsafe_allow_html=True)
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
# SISTEMA DE SIMULACIÓN
# ==========================================================
else:
    # NUEVOS ESTILOS CSS PARA CUBOS BONITOS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #E30613 0%, #1A3A5A 100%);
        padding:20px;
        border-radius:15px;
        text-align:center;
        color:white;
        font-weight:bold;
        font-size:28px;
        margin-bottom:25px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    .cabina {
        background:#34495e;
        color:white;
        text-align:center;
        padding:20px;
        font-weight:bold;
        border-radius:15px 15px 0 0;
        border-bottom:8px solid #95a5a6;
        letter-spacing: 2px;
    }
    /* Estilo para los Cubos (Paquetes) */
    .paquete-card {
        color: white;
        text-align: center;
        padding: 20px 10px;
        margin: 10px;
        border-radius: 12px;
        font-weight: bold;
        box-shadow: inset 0 -5px 0 rgba(0,0,0,0.2), 0 4px 6px rgba(0,0,0,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        transition: transform 0.2s;
    }
    .paquete-card:hover {
        transform: scale(1.02);
    }
    .saldo-badge {
        background: #f8f9fa;
        color: #333;
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 5px;
        margin: 5px;
        font-size: 12px;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">🚛 SIMULADOR DE CARGUE - LOGÍSTICA</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Entrada de Pedido")
        raw_data = st.text_area("Pega la lista de despacho:", height=300, placeholder="Ej: TEJA #6 500")
        if st.button("🔄 Nueva Simulación"):
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
                        pedido_items.append({
                            "tipo": f"REF #{num_ref}",
                            "cant": cant,
                            "peso": cant * info["peso"],
                            "ref": num_ref,
                            "color": info["color"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        # Dashboard de métricas
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Carga Total", f"{peso_total_pedido:,.1f} kg")
        col_m2.metric("Vehículo Sugerido", vh['tipo'])
        col_m3.metric("Ocupación", f"{(peso_total_pedido/vh['capacidad_max']*100):.1f}%")

        st.markdown('<div class="cabina">🚚 FRENTE (CABINA DEL VEHÍCULO)</div>', unsafe_allow_html=True)

        # Lógica de organización
        mapa_visual = []
        saldos = []
        for item in sorted(pedido_items, key=lambda x: PRODUCTOS_BASE[x['ref']]['largo_ft'], reverse=True):
            paq_size = PRODUCTOS_BASE[item['ref']]['paquete']
            completos = item["cant"] // paq_size
            sobra = item["cant"] % paq_size
            
            for _ in range(completos):
                mapa_visual.append(item)
            if sobra > 0:
                saldos.append({"tipo": item["tipo"], "cant": sobra, "color": item["color"]})

        # Renderizado de filas de 2 paquetes
        rows = [mapa_visual[i:i+2] for i in range(0, len(mapa_visual), 2)]
        
        for row in rows:
            c_izq, c_centro1, c_centro2, c_der = st.columns([1, 2, 2, 1])
            
            with c_centro1:
                st.markdown(f'<div class="paquete-card" style="background-color:{row[0]["color"]};">{row[0]["tipo"]}<br>{PRODUCTOS_BASE[row[0]["ref"]]["paquete"]} UND</div>', unsafe_allow_html=True)
            
            with c_centro2:
                if len(row) > 1:
                    st.markdown(f'<div class="paquete-card" style="background-color:{row[1]["color"]};">{row[1]["tipo"]}<br>{PRODUCTOS_BASE[row[1]["ref"]]["paquete"]} UND</div>', unsafe_allow_html=True)
            
            # Colocar saldos a los lados si existen
            with c_izq:
                if saldos:
                    s = saldos.pop(0)
                    st.markdown(f'<div class="saldo-badge" style="border-left: 5px solid {s["color"]};">📦 {s["tipo"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
            with c_der:
                if saldos:
                    s = saldos.pop(0)
                    st.markdown(f'<div class="saldo-badge" style="border-right: 5px solid {s["color"]};">📦 {s["tipo"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        # Si sobran saldos por dibujar
        if saldos:
            st.write("---")
            st.caption("Saldos adicionales en la parte trasera:")
            cols_s = st.columns(len(saldos) if len(saldos) < 5 else 4)
            for idx, s in enumerate(saldos):
                with cols_s[idx % 4]:
                    st.markdown(f'<div class="saldo-badge" style="background:{s["color"]}; color:white;">{s["tipo"]}: {s["cant"]} UND</div>', unsafe_allow_html=True)

    else:
        st.info("👋 ¡Bienvenido! Ingresa los datos del pedido en el panel de la izquierda para ver la distribución de los paquetes de colores.")
