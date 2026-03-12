import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# Base de datos ampliada con todas las variantes posibles
PRODUCTOS = {
    "TEJA FLEXIFORTE #10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
    "TEJA FLEXIFORTE #8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "TEJA #10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
    "TEJA #8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "TEJA #6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "TEJA #5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "TEJA #4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
}

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

st.set_page_config(page_title="Smart Picking PRO", layout="wide")

# --- FUNCION DE LOGIN ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("ETERNIT LOGOS.webp", use_container_width=True)
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Acceso denegado")
        return False
    return True

if login():
    # 2. ESTILOS CSS
    st.markdown("""
    <style>
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 10px; font-weight: bold; border-radius: 5px; }
        .paquete-v { background: #27ae60; color: white; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; }
        .paquete-h { background: #2980b9; color: white; text-align: center; padding: 15px; margin: 5px; border-radius: 4px; font-weight: bold; border: 2px dashed white; }
        .saldo-box { background: #f1c40f; color: black; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; }
        .stMetric { background: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid #E30613; }
    </style>
    """, unsafe_allow_html=True)

    # 3. ENTRADA DE DATOS
    with st.sidebar:
        st.header("📋 Carga de Pedido")
        raw_data = st.text_area("Pegue aquí el pedido desde Excel:", height=250)
        
        if st.button("Limpiar Datos"):
            st.rerun()

    # --- LÓGICA DE PROCESAMIENTO MULTI-REFERENCIA ---
    pedido_items = []
    peso_total_pedido = 0
    
    if raw_data:
        lines = raw_data.strip().split('\n')
        # Ordenamos las llaves de PRODUCTOS por longitud (de mayor a menor)
        # Esto asegura que reconozca "TEJA FLEXIFORTE #10" antes que "TEJA #10"
        lista_ordenada_productos = sorted(PRODUCTOS.keys(), key=len, reverse=True)
        
        for line in lines:
            line_upper = line.upper().strip()
            if not line_upper: continue
            
            for prod_name in lista_ordenada_productos:
                if prod_name in line_upper:
                    # Quitamos el nombre de la teja para que no confunda el # de teja con la cantidad
                    texto_sin_nombre = line_upper.replace(prod_name, "")
                    # Buscamos todos los números que queden en la línea
                    numeros = re.findall(r'\d+', texto_sin_nombre)
                    
                    if numeros:
                        try:
                            # El primer número que sobre en la línea es la cantidad
                            cant = int(numeros[0])
                            peso_item = cant * PRODUCTOS[prod_name]["peso"]
                            pedido_items.append({"tipo": prod_name, "cant": cant, "peso": peso_item})
                            peso_total_pedido += peso_item
                            break # Ya encontró el producto en esta línea, pasa a la siguiente
                        except: pass

    if pedido_items:
        # 4. SELECCIÓN DE VEHÍCULO
        vh_asignado = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        st.markdown(f"### 🚛 Vehículo Sugerido: {vh_asignado['tipo']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Capacidad VH", f"{vh_asignado['capacidad_max']:,.0f} kg")
        c3.metric("Largo Requerido", f"{max([PRODUCTOS[i['tipo']]['largo_ft'] for i in pedido_items])} ft")

        # 5. DISTRIBUCIÓN
        pedido_items_sorted = sorted(pedido_items, key=lambda x: PRODUCTOS[x["tipo"]]["largo_ft"], reverse=True)
        
        mapa_vertical = []
        saldos = []
        
        for item in pedido_items_sorted:
            paq_tam = PRODUCTOS[item["tipo"]]["paquete"]
            completos = item["cant"] // paq_tam
            sobra = item["cant"] % paq_tam
            
            for _ in range(completos):
                mapa_vertical.append({"label": item["tipo"], "cant": paq_tam})
            if sobra > 0:
                saldos.append({"label": item["tipo"], "cant": sobra})

        # 6. MAPA VISUAL
        st.markdown("---")
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        paquetes_render = list(mapa_vertical)
        atravesado = None
        if len(paquetes_render) % 2 != 0:
            atravesado = paquetes_render.pop()

        rows = [paquetes_render[i:i + 2] for i in range(0, len(paquetes_render), 2)]
        
        for row in rows:
            cols = st.columns(4)
            with cols[1]:
                st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]:
                if len(row) > 1:
                    st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)

        if saldos:
            st.markdown("**📦 Saldos (Encima de la carga):**")
            s_cols = st.columns(5)
            for idx, s in enumerate(saldos):
                with s_cols[idx % 5]:
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} und</div>', unsafe_allow_html=True)

        if atravesado:
            st.markdown(f'<div class="paquete-h">📦 PAQUETE HORIZONTAL TRASERO<br>{atravesado["label"]} ({atravesado["cant"]})</div>', unsafe_allow_html=True)
    else:
        st.info("Pega los datos del pedido para ver el desglose.")
