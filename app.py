import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# Base de datos de productos
PRODUCTOS = {
    "TEJA #4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "TEJA #5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "TEJA #6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "TEJA #8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "TEJA #10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

# Base de datos de vehículos
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
        raw_data = st.text_area("Pegue aquí el pedido desde Excel:", placeholder="Ejemplo: TEJA FLEXIFORTE #8 500 unidades")
        
        if st.button("Limpiar Datos"):
            st.rerun()

    # Procesar datos pegados
    pedido_items = []
    peso_total_pedido = 0
    if raw_data:
        lines = raw_data.strip().split('\n')
        for line in lines:
            line_upper = line.upper()
            
            # Buscamos cada producto de nuestra base de datos en la línea
            for prod_name in PRODUCTOS.keys():
                # Esta es la parte clave: busca el nombre (ej: TEJA #5) dentro de la cadena
                if prod_name in line_upper:
                    # Una vez encontrado el nombre, extraemos todos los números de la línea
                    # pero ignoramos el número que es parte del nombre (el #4, #5, etc.)
                    # Usamos una expresión regular para encontrar la cantidad
                    linea_sin_nombre = line_upper.replace(prod_name, "")
                    numeros_encontrados = re.findall(r'\d+', linea_sin_nombre)
                    
                    if numeros_encontrados:
                        try:
                            # Tomamos el primer número que aparezca después de quitar el nombre
                            cant = int(numeros_encontrados[0])
                            peso_item = cant * PRODUCTOS[prod_name]["peso"]
                            pedido_items.append({"tipo": prod_name, "cant": cant, "peso": peso_item})
                            peso_total_pedido += peso_item
                            break # Pasar a la siguiente línea
                        except: pass

    if pedido_items:
        # 4. SELECCIÓN AUTOMÁTICA DE VEHÍCULO
        vh_asignado = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        # UI DE RESUMEN
        st.markdown(f"### 🚛 Vehículo Sugerido: {vh_asignado['tipo']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Capacidad VH", f"{vh_asignado['capacidad_max']:,.0f} kg")
        c3.metric("Largo Disponible", f"{vh_asignado['largo_planchon_ft']} ft")

        # 5. LÓGICA DE DISTRIBUCIÓN
        pedido_items = sorted(pedido_items, key=lambda x: PRODUCTOS[x["tipo"]]["largo_ft"], reverse=True)
        
        mapa_vertical = []
        saldos = []
        
        for item in pedido_items:
            paq_tam = PRODUCTOS[item["tipo"]]["paquete"]
            completos = item["cant"] // paq_tam
            sobra = item["cant"] % paq_tam
            
            for _ in range(completos):
                mapa_vertical.append({"label": f"{item['tipo']}", "cant": paq_tam})
            if sobra > 0:
                saldos.append({"label": f"S. {item['tipo']}", "cant": sobra})

        # 6. VISUALIZACIÓN DEL MAPA DE CARGA
        st.markdown("---")
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        # Lógica de dibujo del planchón
        paquetes_lista = list(mapa_vertical)
        atravesado = None
        if len(paquetes_lista) % 2 != 0:
            atravesado = paquetes_lista.pop()

        rows = [paquetes_lista[i:i + 2] for i in range(0, len(paquetes_lista), 2)]
        
        for row in rows:
            cols = st.columns(4)
            with cols[1]:
                if len(row) > 0: st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]:
                if len(row) > 1: st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)

        if saldos:
            st.markdown("**📦 Saldos (Cargar encima de los paquetes):**")
            s_cols = st.columns(len(saldos) if len(saldos) < 5 else 5)
            for idx, s in enumerate(saldos):
                with s_cols[idx % 5]:
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>Unidades: {s["cant"]}</div>', unsafe_allow_html=True)

        if atravesado:
            st.markdown(f'<div class="paquete-h">📦 PAQUETE HORIZONTAL (ATRAVESADO TRASERO)<br>{atravesado["label"]} ({atravesado["cant"]})</div>', unsafe_allow_html=True)

    else:
        st.info("Escriba o pegue un pedido en la barra lateral para generar el mapa de carga.")
