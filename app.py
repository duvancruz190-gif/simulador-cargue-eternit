import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN Y LÓGICA DE NEGOCIO
# -----------------------------
st.set_page_config(page_title="Eternit - Simulador de Cargue Inteligente", page_icon="🚛", layout="wide")

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
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; margin-bottom:10px; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:10px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; min-height: 80px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:10px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #7d6608; min-height: 80px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
    .pies-tag { font-size: 11px; background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 10px; margin-top: 5px; }
    .footer-total { background: #f0f2f6; padding: 10px; text-align: center; border-radius: 0 0 5px 5px; font-weight: 800; border: 1px solid #d1d3d8; color: #1A3A5A; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: ENTRADA DE DATOS ---
with st.sidebar:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_YF8S_58V5O6C_k-m036Yp4A_t35L8GfFsg&s", width=200) # Logo genérico Eternit
    st.header("📋 Entrada de Pedido")
    raw_data = st.text_area("Pegue el pedido completo:", height=300, placeholder="TEJA #10 560\nTEJA #8 300...")
    if st.button("Limpiar Simulador"): st.rerun()

if raw_data:
    pedido_procesado = []
    peso_total_kg = 0
    
    # Algoritmo de extracción de datos
    lines = raw_data.strip().split("\n")
    for line in lines:
        line = line.upper()
        ref_match = re.search(r'#(\d+)', line)
        if ref_match:
            ref = ref_match.group(1)
            if ref in PRODUCTOS_BASE:
                # Extraer cantidad ignorando el #Ref
                clean_line = line.replace(f"#{ref}", "")
                nums = re.findall(r'\d+', clean_line)
                if nums:
                    cant = int(nums[-1])
                    info = PRODUCTOS_BASE[ref]
                    pedido_procesado.append({
                        "ref": ref, "cant": cant, "largo": info["largo_ft"], 
                        "paq_std": info["paquete"], "peso_u": info["peso"]
                    })
                    peso_total_kg += cant * info["peso"]

    if pedido_procesado:
        # 1. Selección de Vehículo
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_kg), VEHICULOS[-1])
        
        # 2. ALGORITMO DE DISTRIBUCIÓN (EL "CEREBRO")
        carril_izq = []
        carril_der = []
        largo_izq = 0
        largo_der = 0

        # Ordenar por largo descendente para estabilidad
        pedido_sorted = sorted(pedido_procesado, key=lambda x: x['largo'], reverse=True)

        for item in pedido_sorted:
            unidades_restantes = item['cant']
            
            # Repartir unidades mientras queden
            while unidades_restantes > 0:
                # Determinar en qué carril poner el siguiente bulto (el que sea más corto)
                # Si son iguales, prioriza izquierda para mantener orden
                objetivo = "IZQ" if largo_izq <= largo_der else "DER"
                
                # ¿Qué tipo de bulto armar?
                if unidades_restantes >= item['paq_std']:
                    cant_bulto = item['paq_std']
                    tipo_bulto = "verde"
                else:
                    # Regla de los 60: Si es saldo, máximo 60
                    cant_bulto = min(unidades_restantes, 60)
                    tipo_bulto = "amarillo"
                
                bulto_data = {
                    "label": f"TEJA #{item['ref']}", 
                    "cant": cant_bulto, 
                    "largo": item['largo'], 
                    "color": tipo_bulto
                }

                if objetivo == "IZQ":
                    carril_izq.append(bulto_data)
                    largo_izq += item['largo']
                else:
                    carril_der.append(bulto_data)
                    largo_der += item['largo']
                
                unidades_restantes -= cant_bulto

        # --- VISUALIZACIÓN ---
        col1, col2, col3 = st.columns(3)
        col1.metric("PESO TOTAL", f"{peso_total_kg:,.0f} kg")
        col2.metric("VEHÍCULO", vh['tipo'])
        col3.metric("LARGO MÁX", f"{max(largo_izq, largo_der)} / {vh['largo_planchon_ft']} ft")

        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        v_izq, v_der = st.columns(2)
        
        with v_izq:
            for b in carril_izq:
                tag = "paquete-v" if b['color'] == "verde" else "saldo-box"
                st.markdown(f'<div class="{tag}">{b["label"]}<br>{b["cant"]} UND<div class="pies-tag">{b["largo"]} ft</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="footer-total">{largo_izq} PASOS (ft)</div>', unsafe_allow_html=True)

        with v_der:
            for b in carril_der:
                tag = "paquete-v" if b['color'] == "verde" else "saldo-box"
                st.markdown(f'<div class="{tag}">{b["label"]}<br>{b["cant"]} UND<div class="pies-tag">{b["largo"]} ft</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="footer-total">{largo_der} PASOS (ft)</div>', unsafe_allow_html=True)

        # ALERTAS FINALES
        if max(largo_izq, largo_der) > vh['largo_planchon_ft']:
            st.error(f"⚠️ CAPACIDAD FÍSICA EXCEDIDA: El cargue mide {max(largo_izq, largo_der)} ft. El vehículo solo tiene {vh['largo_planchon_ft']} ft.")
        if peso_total_kg > vh['capacidad_max']:
            st.warning(f"⚖️ SOBRECARGA: El peso supera el límite del vehículo.")
