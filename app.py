import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# Base de datos actualizada (Reconoce nombres largos y variantes)
PRODUCTOS = {
    "TEJA FLEXIFORTE #8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
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

st.set_page_config(page_title="Smart Picking PRO - Eternit", layout="wide")

# --- FUNCION DE LOGIN ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_r_n6T-0Oid7Z96LhOq-qT1VjL7L7PqL2Nw&s", use_container_width=True)
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
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 10px; font-weight: bold; border-radius: 5px; margin-bottom: 10px; }
        .paquete-v { background: #27ae60; color: white; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; border: 1px solid #1e8449; }
        .paquete-h { background: #2980b9; color: white; text-align: center; padding: 15px; margin: 5px; border-radius: 4px; font-weight: bold; border: 2px dashed white; }
        .saldo-box { background: #f1c40f; color: black; text-align: center; padding: 10px; margin: 2px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .stMetric { background: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid #E30613; }
    </style>
    """, unsafe_allow_html=True)

    # 3. ENTRADA DE DATOS (RECONOCIMIENTO ROBUSTO)
    with st.sidebar:
        st.header("📋 Carga de Pedido")
        st.info("Puede pegar datos como: 'TEJA FLEXIFORTE #8 500 UNIDADES'")
        raw_data = st.text_area("Pegue aquí el pedido desde Excel:", height=200, placeholder="Ejemplo:\nTEJA FLEXIFORTE #8 260\nTEJA #4 130")
        
        if st.button("Limpiar Datos"):
            st.rerun()

    # PROCESAMIENTO MEJORADO
    pedido_items = []
    peso_total_pedido = 0
    
    if raw_data:
        lines = raw_data.strip().split('\n')
        for line in lines:
            line_upper = line.upper()
            # Ordenamos las llaves por longitud para que busque primero "TEJA FLEXIFORTE #8" antes que "TEJA #8"
            for nombre_prod in sorted(PRODUCTOS.keys(), key=len, reverse=True):
                if nombre_prod in line_upper:
                    # Extraer números que queden en la línea después de quitar el nombre del producto
                    limpio = line_upper.replace(nombre_prod, "")
                    numeros = re.findall(r'\d+', limpio)
                    if numeros:
                        try:
                            cant = int(numeros[0])
                            peso_item = cant * PRODUCTOS[nombre_prod]["peso"]
                            pedido_items.append({"tipo": nombre_prod, "cant": cant, "peso": peso_item})
                            peso_total_pedido += peso_item
                            break # Encontró el producto, pasa a la siguiente línea
                        except: pass

    if pedido_items:
        # 4. SELECCIÓN AUTOMÁTICA DE VEHÍCULO
        vh_asignado = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        # UI DE RESUMEN
        st.markdown(f"### 🚛 Vehículo Sugerido: {vh_asignado['tipo']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Capacidad Máx", f"{vh_asignado['capacidad_max']:,.0f} kg")
        c3.metric("Carga Utilizada", f"{(peso_total_pedido/vh_asignado['capacidad_max'])*100:.1f}%")

        # 5. LÓGICA DE DISTRIBUCIÓN
        # Ordenar por largo (más largo adelante)
        pedido_items = sorted(pedido_items, key=lambda x: PRODUCTOS[x["tipo"]]["largo_ft"], reverse=True)
        
        mapa_vertical = []
        saldos = []
        
        for item in pedido_items:
            paq_tam = PRODUCTOS[item["tipo"]]["paquete"]
            completos = item["cant"] // paq_tam
            sobra = item["cant"] % paq_tam
            
            for _ in range(completos):
                mapa_vertical.append({"label": item["tipo"], "cant": paq_tam})
            if sobra > 0:
                saldos.append({"label": item["tipo"], "cant": sobra})

        # 6. VISUALIZACIÓN DEL MAPA DE CARGA
        st.markdown("---")
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        # El planchón se divide en filas de 2 paquetes
        # Copiamos para no afectar la lista original
        paquetes_render = list(mapa_vertical)
        
        # Si hay un número impar de paquetes, el último será "Atravesado"
        atravesado = None
        if len(paquetes_render) % 2 != 0:
            atravesado = paquetes_render.pop()

        # Render Vertical (Parejas)
        for i in range(0, len(paquetes_render), 2):
            cols = st.columns([1, 2, 2, 1]) # Centrado
            with cols[1]:
                st.markdown(f'<div class="paquete-v">📦 {paquetes_render[i]["label"]}<br><b>{paquetes_render[i]["cant"]} UN</b></div>', unsafe_allow_html=True)
            with cols[2]:
                if i+1 < len(paquetes_render):
                    st.markdown(f'<div class="paquete-v">📦 {paquetes_render[i+1]["label"]}<br><b>{paquetes_render[i+1]["cant"]} UN</b></div>', unsafe_allow_html=True)

        # Render Paquete Atravesado (si existe)
        if atravesado:
            st.markdown(f'<div class="paquete-h">📦 PAQUETE HORIZONTAL TRASERO<br>{atravesado["label"]} ({atravesado["cant"]} UN)</div>', unsafe_allow_html=True)

        # Render Saldos
        if saldos:
            st.markdown("### 📦 Saldos (Cargar sueltas encima)")
            s_cols = st.columns(min(len(saldos), 4))
            for idx, s in enumerate(saldos):
                with s_cols[idx % 4]:
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>Cant: {s["cant"]}</div>', unsafe_allow_html=True)
        
        # Tabla resumen para exportar o revisar
        with st.expander("Ver detalle de cantidades"):
            st.table(pd.DataFrame(pedido_items))

    else:
        st.warning("Aún no hay datos para procesar. Pegue el pedido en la barra lateral.")
