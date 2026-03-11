import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

PRODUCTOS = {
    "#4": {"id": "TEJA #4", "peso": 11.82, "paquete": 130, "largo_ft": 4},
    "#5": {"id": "TEJA #5", "peso": 14.77, "paquete": 130, "largo_ft": 5},
    "#6": {"id": "TEJA #6", "peso": 17.72, "paquete": 130, "largo_ft": 6},
    "#8": {"id": "TEJA #8", "peso": 23.63, "paquete": 130, "largo_ft": 8},
    "#10": {"id": "TEJA #10", "peso": 29.54, "paquete": 100, "largo_ft": 10},
}

PESO_ESTIBA = 30 # kg por bulto

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

st.set_page_config(page_title="Smart Picking PRO", layout="wide")

def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try: st.image("ETERNIT LOGOS.webp", use_container_width=True)
            except: st.title("ETERNIT")
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Acceso denegado")
        return False
    return True

if login():
    st.markdown("""
    <style>
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 10px; font-weight: bold; border-radius: 5px; margin-bottom: 10px; }
        .paquete-v { background: #27ae60; color: white; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; font-weight: bold; min-height: 60px; }
        .saldo-box { background: #f1c40f; color: black; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; font-weight: bold; min-height: 60px; border: 2px solid #d4ac0d; }
        .paquete-h { background: #2980b9; color: white; text-align: center; padding: 15px; margin: 5px; border-radius: 4px; font-weight: bold; border: 2px dashed white; }
        .stMetric { background: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid #E30613; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Carga de Pedido")
        raw_data = st.text_area("Pegue aquí el pedido:", placeholder="Ejemplo:\nTEJA FLEXIFORTE #5 200\nTEJA #4 150")
        if st.button("Limpiar Datos"): st.rerun()

    pedido_items = []
    peso_total_pedido = 0
    total_estibas = 0

    if raw_data:
        lines = raw_data.strip().split('\n')
        for line in lines:
            line_upper = line.upper()
            parts = line.split()
            if not parts: continue
            
            for key, data in PRODUCTOS.items():
                if key in line_upper:
                    try:
                        cant = int(parts[-1])
                        completos = cant // data["paquete"]
                        sobra = cant % data["paquete"]
                        
                        estibas_linea = completos + (1 if sobra > 0 else 0)
                        peso_material = cant * data["peso"]
                        
                        peso_total_pedido += peso_material + (estibas_linea * PESO_ESTIBA)
                        total_estibas += estibas_linea
                        
                        pedido_items.append({
                            "label": data["id"], 
                            "paq": completos, 
                            "sobra": sobra, 
                            "largo": data["largo_ft"],
                            "paq_tam": data["paquete"]
                        })
                    except: pass

    if pedido_items:
        vh_asignado = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        st.markdown(f"### 🚛 Vehículo Sugerido: {vh_asignado['tipo']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total (+Estibas)", f"{peso_total_pedido:,.1f} kg")
        c2.metric("Total Bultos", total_estibas)
        c3.metric("Largo Vehículo", f"{vh_asignado['largo_planchon_ft']} ft")

        # 5. ORGANIZACIÓN DE BLOQUES (Verdes y Amarillos mezclados)
        bloques_totales = []
        pedido_items = sorted(pedido_items, key=lambda x: x["largo"], reverse=True)

        for item in pedido_items:
            # Añadir paquetes completos (Verdes)
            for _ in range(item["paq"]):
                bloques_totales.append({"label": f"{item['label']}<br>{item['paq_tam']} UN", "tipo": "verde"})
            # Añadir saldos (Amarillos)
            if item["sobra"] > 0:
                bloques_totales.append({"label": f"SALDO {item['label']}<br>{item['sobra']} UN", "tipo": "amarillo"})

        # 6. VISUALIZACIÓN
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        # Manejo de paquete atravesado si el total es impar
        atravesado = None
        if len(bloques_totales) % 2 != 0:
            atravesado = bloques_totales.pop()

        # Dibujar en 2 columnas (Izquierda y Derecha)
        for i in range(0, len(bloques_totales), 2):
            col_izq, col_der = st.columns(2)
            for idx, col_sitio in enumerate([col_izq, col_der]):
                with col_sitio:
                    b = bloques_totales[i + idx]
                    clase = "paquete-v" if b["tipo"] == "verde" else "saldo-box"
                    st.markdown(f'<div class="{clase}">{b["label"]}</div>', unsafe_allow_html=True)

        if atravesado:
            clase_h = "paquete-h" if atravesado["tipo"] == "verde" else "saldo-box"
            st.markdown(f'<div class="{clase_h}">📦 CARGA TRASERA (ATRAVESADA)<br>{atravesado["label"]}</div>', unsafe_allow_html=True)
            
    else:
        st.info("💡 Pegue su pedido en el lateral para generar el mapa de carga.")
