import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(
    page_title="Simulador de Cargue 3D Style",
    page_icon="🚛",
    layout="wide"
)

# Colores dinámicos por referencia (Tipo EasyCargo)
COLORES_REF = {
    "10": {"bg": "#27ae60", "border": "#1e8449"},  # Verde
    "8":  {"bg": "#2980b9", "border": "#1b4f72"},  # Azul
    "6":  {"bg": "#f39c12", "border": "#d35400"},  # Naranja
    "5":  {"bg": "#8e44ad", "border": "#5b2c6f"},  # Morado
    "4":  {"bg": "#7f8c8d", "border": "#2c3e50"},  # Gris
}

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000},
    {"tipo": "SENCILLO", "capacidad_max": 10000},
    {"tipo": "MULA", "capacidad_max": 34000},
]

# -----------------------------
# ESTILOS CSS PERSONALIZADOS (Efecto Bloque 3D)
# -----------------------------
st.markdown("""
<style>
    .planchon {
        background: #f8f9fa;
        border: 4px solid #34495e;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .cabina-v2 {
        background: linear-gradient(180deg, #1A3A5A 0%, #2c3e50 100%);
        color: white;
        text-align: center;
        padding: 15px;
        font-weight: bold;
        border-radius: 15px 15px 0 0;
        letter-spacing: 2px;
        border-bottom: 8px solid #95a5a6;
    }
    .bloque-3d {
        color: white;
        text-align: center;
        padding: 15px 5px;
        margin: 5px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 14px;
        box-shadow: inset -4px -4px 0px rgba(0,0,0,0.2), 3px 3px 5px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 80px;
    }
    .saldo-box-v2 {
        background: #f1c40f;
        color: #2c3e50;
        text-align: center;
        padding: 10px 2px;
        margin: 5px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 900;
        border-bottom: 3px solid #f39c12;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LÓGICA DE APLICACIÓN
# -----------------------------
with st.sidebar:
    st.header("📋 Entrada de Pedido")
    raw_data = st.text_area("Pega el pedido de Eternit", height=200, placeholder="FLEXIFORTE #10 500\nFLEXIFORTE #8 200")
    if st.button("Limpiar Datos"): st.rerun()

pedido_items = []
peso_total = 0

if raw_data:
    lines = raw_data.strip().split("\n")
    for line in lines:
        match_ref = re.search(r'#(\d+)', line)
        if match_ref:
            ref = match_ref.group(1)
            if ref in PRODUCTOS_BASE:
                nums = re.findall(r'\d+', line.replace(f"#{ref}", ""))
                if nums:
                    cant = int(nums[-1])
                    peso_total += cant * PRODUCTOS_BASE[ref]["peso"]
                    pedido_items.append({"tipo": f"FLEX. #{ref}", "cant": cant, "ref": ref})

if pedido_items:
    vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total), VEHICULOS[-1])
    
    # Dashboard de métricas
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("PESO CARGA", f"{peso_total:,.0f} kg")
    col_b.metric("VEHÍCULO", vh["tipo"])
    col_c.metric("CAPACIDAD", f"{vh['capacidad_max']} kg")

    st.markdown('<div class="cabina-v2">FRONTAL - CABINA DEL VEHÍCULO</div>', unsafe_allow_html=True)
    
    # Contenedor del planchón
    st.markdown('<div class="planchon">', unsafe_allow_html=True)
    
    # Organizar paquetes
    paquetes_completos = []
    saldos = []
    
    for item in pedido_items:
        cap_paq = PRODUCTOS_BASE[item["ref"]]["paquete"]
        completos = item["cant"] // cap_paq
        sobra = item["cant"] % cap_paq
        
        for _ in range(completos):
            paquetes_completos.append(item)
        if sobra > 0:
            saldos.append({"tipo": item["tipo"], "cant": sobra, "ref": item["ref"]})

    # Renderizado de filas (2 paquetes por fila + saldos laterales)
    rows = [paquetes_completos[i:i+2] for i in range(0, len(paquetes_completos), 2)]
    
    for row in rows:
        cols = st.columns([0.8, 1.5, 1.5, 0.8])
        
        # Saldo Izquierdo
        with cols[0]:
            if saldos:
                s = saldos.pop(0)
                st.markdown(f'<div class="saldo-box-v2">{s["tipo"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
        
        # Paquete Central 1
        with cols[1]:
            ref_id = row[0]["ref"]
            color = COLORES_REF.get(ref_id, {"bg": "#7f8c8d", "border": "#2c3e50"})
            st.markdown(f'''<div class="bloque-3d" style="background:{color['bg']}; border-left: 8px solid {color['border']};">
                {row[0]["tipo"]}<br>({PRODUCTOS_BASE[ref_id]["paquete"]} UND)</div>''', unsafe_allow_html=True)
        
        # Paquete Central 2
        with cols[2]:
            if len(row) > 1:
                ref_id_2 = row[1]["ref"]
                color2 = COLORES_REF.get(ref_id_2, {"bg": "#7f8c8d", "border": "#2c3e50"})
                st.markdown(f'''<div class="bloque-3d" style="background:{color2['bg']}; border-left: 8px solid {color2['border']};">
                    {row[1]["tipo"]}<br>({PRODUCTOS_BASE[ref_id_2]["paquete"]} UND)</div>''', unsafe_allow_html=True)
        
        # Saldo Derecho
        with cols[3]:
            if saldos:
                s = saldos.pop(0)
                st.markdown(f'<div class="saldo-box-v2">{s["tipo"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#95a5a6; margin-top:10px;">⬇ TRASERA / ZONA DE CARGA ⬇</div>', unsafe_allow_html=True)

else:
    st.info("👋 Por favor, ingresa los datos del pedido en el panel lateral.")
