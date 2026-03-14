import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN Y LÍMITES REALES (SEGÚN TU TABLA)
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue", layout="wide")

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

# Datos exactos de tu imagen
VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

# -----------------------------
# ESTILOS VISUALES (RESURRECCIÓN DEL DISEÑO ORIGINAL)
# -----------------------------
st.markdown("""
<style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
    .paquete-v { background:#27ae60; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #1e8449; }
    .paquete-h { background:#2980b9; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:85%; }
    .saldo-box { background:#f1c40f; color:#2c3e50; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #d4ac0d; }
    .error-logistica { color: #E30613; font-weight: bold; background: #ffe6e6; padding: 10px; border-radius: 5px; border: 1px solid #E30613; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LÓGICA DE CARGUE
# -----------------------------
with st.sidebar:
    st.header("📋 Pedido")
    raw_data = st.text_area("Pegue el pedido aquí", height=250)
    if st.button("Limpiar"): st.rerun()

if raw_data:
    items = []
    peso_total = 0
    lines = raw_data.strip().split("\n")
    for line in lines:
        match = re.search(r'#(\d+)', line)
        if match:
            ref = match.group(1)
            numeros = re.findall(r'\d+', line.replace(f"#{ref}", ""))
            if numeros:
                cant = int(numeros[-1])
                info = PRODUCTOS_BASE[ref]
                items.append({"ref": ref, "cant": cant, "largo": info["largo_ft"]})
                peso_total += cant * info["peso"]

    if items:
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total), VEHICULOS[-1])
        st.write(f"### Vehículo Sugerido: {vh['tipo']} (Largo: {vh['largo_planchon_ft']} ft)")
        
        # Clasificación
        verdes = []
        amarillos = []
        for it in sorted(items, key=lambda x: x['largo'], reverse=True):
            paq_std = PRODUCTOS_BASE[it['ref']]['paquete']
            for _ in range(it['cant'] // paq_std):
                verdes.append({"label": f"FLEX. #{it['ref']}", "largo": it['largo'], "cant": paq_std})
            sobra = it['cant'] % paq_std
            while sobra > 0:
                c = min(sobra, 60)
                amarillos.append({"label": f"FLEX. #{it['ref']}", "largo": it['largo'], "cant": c})
                sobra -= c

        # Estructura de filas (Verdes en el centro, amarillos a los lados)
        atravesado = len(verdes) % 2 != 0
        v_pares = verdes[:-1] if atravesado else verdes
        v_final = verdes[-1] if atravesado else None
        
        filas_verdes = [v_pares[i:i+2] for i in range(0, len(v_pares), 2)]
        
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        # DIBUJO DE FILAS
        for fila in filas_verdes:
            cols = st.columns([1, 1.5, 1.5, 1])
            
            # Saldo Izquierdo
            with cols[0]:
                if amarillos:
                    s = amarillos.pop(0)
                    if s['largo'] > fila[0]['largo']: # ALERTA DE SEGURIDAD
                        st.markdown(f'<div class="error-logistica">⚠️ #{s["label"][-1]} es muy larga para base #{fila[0]["label"][-1]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="saldo-box">SALDO<br>{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
            
            # Centro Verde
            with cols[1]: st.markdown(f'<div class="paquete-v">{fila[0]["label"]}<br>({fila[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]: 
                if len(fila) > 1: st.markdown(f'<div class="paquete-v">{fila[1]["label"]}<br>({fila[1]["cant"]})</div>', unsafe_allow_html=True)
            
            # Saldo Derecho
            with cols[3]:
                if amarillos:
                    s = amarillos.pop(0)
                    if len(fila) > 1 and s['largo'] > fila[1]['largo']:
                         st.markdown(f'<div class="error-logistica">⚠️ #{s["label"][-1]} es muy larga</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="saldo-box">SALDO<br>{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        # PAQUETE AZUL (Siempre cierra la estructura verde)
        if v_final:
            st.markdown(f'<div class="paquete-h">📦 PAQUETE ATRAVESADO (4 PASOS)<br>{v_final["label"]} ({v_final["cant"]} UND)</div>', unsafe_allow_html=True)

        # SALDOS SOBRANTES (Solo si no cupieron arriba)
        if amarillos:
            st.write("---")
            st.caption("Saldos adicionales al final del planchón:")
            cols_fin = st.columns(4)
            for i, s in enumerate(amarillos):
                with cols_fin[i % 4]:
                    st.markdown(f'<div class="saldo-box">PISO<br>{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

else:
    st.info("Pegue un pedido para generar el plano de carga.")
