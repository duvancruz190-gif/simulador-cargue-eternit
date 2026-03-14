import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue Balanceado", page_icon="🚛", layout="wide")

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

# --- ESTILOS ---
st.markdown("""
<style>
.cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
.paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; min-height: 80px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
.saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #7d6608; }
.footer-pies { background: #f0f2f6; padding: 5px; text-align: center; border-radius: 5px; font-weight: bold; border: 1px solid #d1d3d8; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📋 Pedido")
    raw_data = st.text_area("Pegue el pedido aquí", height=250)
    if st.button("Limpiar"): st.rerun()

pedido_items = []
if raw_data:
    lines = raw_data.strip().split("\n")
    for line in lines:
        match = re.search(r'#(\d+)', line)
        if match:
            ref = match.group(1)
            nums = re.findall(r'\d+', line.replace(f"#{ref}", ""))
            if nums:
                cant = int(nums[-1])
                pedido_items.append({"ref": ref, "cant": cant, **PRODUCTOS_BASE[ref]})

if pedido_items:
    # 1. Procesar todo el pedido para obtener bultos
    carril_izq = []
    carril_der = []
    todos_saldos = []
    
    # Ordenar de mayor a menor largo para estabilidad
    pedido_items = sorted(pedido_items, key=lambda x: x['largo_ft'], reverse=True)

    for item in pedido_items:
        paq_nom = item['paquete']
        num_paquetes = item['cant'] // paq_nom
        unidades_sueltas = item['cant'] % paq_nom
        
        # SI HAY PAQUETES: Intentar emparejar
        while num_paquetes >= 2:
            p_izq = {"label": f"TEJA #{item['ref']}", "cant": paq_nom, "largo": item['largo_ft']}
            p_der = {"label": f"TEJA #{item['ref']}", "cant": paq_nom, "largo": item['largo_ft']}
            carril_izq.append(p_izq)
            carril_der.append(p_der)
            num_paquetes -= 2
        
        # SI QUEDA 1 SOLO PAQUETE (IMPAR): Se parte y se vuelve saldo
        if num_paquetes == 1:
            # Dividimos el paquete en dos saldos de la mitad para equilibrar
            mitad = paq_nom // 2
            resto = paq_nom - mitad
            todos_saldos.append({"label": f"TEJA #{item['ref']}", "cant": mitad})
            todos_saldos.append({"label": f"TEJA #{item['ref']}", "cant": resto})
            
        # AGREGAR LAS UNIDADES SUELTAS ORIGINALES A SALDOS
        if unidades_sueltas > 0:
            todos_saldos.append({"label": f"TEJA #{item['ref']}", "cant": unidades_sueltas})

    # Calcular largos
    total_ft = sum([p['largo'] for p in carril_izq])
    vh = next((v for v in VEHICULOS if v["largo_planchon_ft"] >= total_ft), VEHICULOS[-1])

    # --- DIBUJAR ---
    st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
    
    col_s1, col_p1, col_p2, col_s2 = st.columns([1, 2, 2, 1])
    
    # Renderizar Paquetes Verdes (Simétricos)
    with col_p1:
        for p in carril_izq:
            st.markdown(f'<div class="paquete-v">{p["label"]}<br>({p["cant"]})<br>{p["largo"]} ft</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="footer-pies">{total_ft} ft</div>', unsafe_allow_html=True)
        
    with col_p2:
        for p in carril_der:
            st.markdown(f'<div class="paquete-v">{p["label"]}<br>({p["cant"]})<br>{p["largo"]} ft</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="footer-pies">{total_ft} ft</div>', unsafe_allow_html=True)

    # Renderizar Saldos (Amarillos) repartidos a los lados
    with col_s1:
        for i in range(0, len(todos_saldos), 2):
            s = todos_saldos[i]
            st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
            
    with col_s2:
        for i in range(1, len(todos_saldos), 2):
            s = todos_saldos[i]
            st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

    if total_ft > vh['largo_planchon_ft']:
        st.error(f"⚠️ El cargue mide {total_ft} ft. Supera los {vh['largo_planchon_ft']} ft del {vh['tipo']}")
    else:
        st.success(f"✅ Cargue Balanceado en {vh['tipo']}")
