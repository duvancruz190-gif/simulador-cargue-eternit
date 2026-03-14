import streamlit as st
import pandas as pd
import re

# ==========================================================
# 1. CONFIGURACIÓN Y DATOS MAESTROS
# ==========================================================

st.set_page_config(page_title="Simulador de Cargue", page_icon="🚛", layout="wide")

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
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000},
    {"tipo": "MULA", "capacidad_max": 34000},
]

# ==========================================================
# 2. LÓGICA DE NEGOCIO (EL "CORE")
# ==========================================================

def procesar_pedido(raw_data):
    """Extrae datos del texto y calcula pesos."""
    pedido_items = []
    peso_total = 0
    
    lines = raw_data.strip().split("\n")
    for line in lines:
        line_upper = line.upper().strip()
        match_ref = re.search(r'#(\d+)', line_upper)
        if match_ref:
            ref = match_ref.group(1)
            if ref in PRODUCTOS_BASE:
                numeros = re.findall(r'\d+', line_upper.replace(f"#{ref}", ""))
                if numeros:
                    cant = int(numeros[-1])
                    info = PRODUCTOS_BASE[ref]
                    nombre = f"FLEX. #{ref}" if "FLEXIFORTE" in line_upper else f"TEJA #{ref}"
                    pedido_items.append({
                        "tipo": nombre, "cant": cant, 
                        "peso": cant * info["peso"], "ref": ref
                    })
                    peso_total += cant * info["peso"]
    return pedido_items, peso_total

def distribuir_paquetes(pedido_items):
    """Calcula la disposición de paquetes y saldos."""
    # Ordenar por largo (estabilidad del camión)
    items_sorted = sorted(pedido_items, key=lambda x: PRODUCTOS_BASE[x['ref']]['largo_ft'], reverse=True)
    
    paquetes_v = []
    saldos = []

    for item in items_sorted:
        paq_size = PRODUCTOS_BASE[item['ref']]['paquete']
        completos = item["cant"] // paq_size
        sobra = item["cant"] % paq_size

        for _ in range(completos):
            paquetes_v.append({"label": item["tipo"], "cant": paq_size})
        
        while sobra > 0:
            cant_s = min(sobra, 60)
            saldos.append({"label": item["tipo"], "cant": cant_s})
            sobra -= cant_s

    atravesado = paquetes_v.pop() if len(paquetes_v) % 2 != 0 else None
    filas = [paquetes_v[i:i+2] for i in range(0, len(paquetes_v), 2)]
    
    return filas, saldos, atravesado

# ==========================================================
# 3. INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================================

# Estilos CSS
st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:10px; border-radius:8px 8px 0 0; font-weight:bold; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:10px; margin:2px; border-radius:4px; font-size:12px; }
    .paquete-h { background:#1b4f72; color:white; text-align:center; padding:15px; margin-top:10px; border-radius:4px; border:2px dashed white; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:5px; margin:2px; border-radius:4px; font-size:10px; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("📋 Entrada de Pedido")
    raw_input = st.text_area("Pegue el pedido aquí:", height=250, placeholder="TEJA #5 500...")
    if st.button("Limpiar Todo"): st.rerun()

if raw_input:
    items, peso_total = procesar_pedido(raw_input)
    
    if items:
        # Selección de vehículo
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total), VEHICULOS[-1])
        
        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total:,.1f} kg")
        c2.metric("Vehículo", vh['tipo'])
        c3.metric("Capacidad", f"{vh['capacidad_max']} kg")

        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        # Distribución
        filas, saldos, trasero = distribuir_paquetes(items)
        saldos_copy = list(saldos)

        for fila in filas:
            cols = st.columns([1, 2, 2, 1])
            with cols[0]:
                if saldos_copy:
                    s = saldos_copy.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UN</div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div class="paquete-v">{fila[0]["label"]}<br>({fila[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f'<div class="paquete-v">{fila[1]["label"]}<br>({fila[1]["cant"]})</div>', unsafe_allow_html=True)
            with cols[3]:
                if saldos_copy:
                    s = saldos_copy.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UN</div>', unsafe_allow_html=True)

        if trasero:
            st.markdown(f'<div class="paquete-h">📦 PAQUETE TRASERO: {trasero["label"]} ({trasero["cant"]} UN)</div>', unsafe_allow_html=True)
            
        # Mostrar saldos restantes si sobran
        if saldos_copy:
            st.caption("Saldos adicionales:")
            st.write(", ".join([f"{s['label']} ({s['cant']})" for s in saldos_copy]))
    else:
        st.warning("No se detectaron productos válidos. Use el formato: NOMBRE #REF CANTIDAD")
else:
    st.info("Esperando datos del pedido...")
