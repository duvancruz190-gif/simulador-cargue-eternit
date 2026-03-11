import streamlit as st

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

PRODUCTOS = {
    "#4": {"nombre": "TEJA #4", "peso": 11.82, "paquete": 130, "largo_ft": 4},
    "#5": {"nombre": "TEJA #5", "peso": 14.77, "paquete": 130, "largo_ft": 5},
    "#6": {"nombre": "TEJA #6", "peso": 17.72, "paquete": 130, "largo_ft": 6},
    "#8": {"nombre": "TEJA #8", "peso": 23.63, "paquete": 130, "largo_ft": 8},
    "#10": {"nombre": "TEJA #10", "peso": 29.54, "paquete": 100, "largo_ft": 10},
}

PESO_ESTIBA = 30 # kg por estiba
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
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 15px; font-weight: bold; border-radius: 10px 10px 0 0; }
        .paquete-v { background: #27ae60; color: white; text-align: center; padding: 10px; margin: 4px; border-radius: 6px; font-weight: bold; min-height: 60px; }
        .saldo-v { background: #f1c40f; color: black; text-align: center; padding: 10px; margin: 4px; border-radius: 6px; font-weight: bold; min-height: 60px; border: 2px solid #d4ac0d; }
        .paquete-h { background: #2980b9; color: white; text-align: center; padding: 15px; margin: 10px 4px; border-radius: 8px; font-weight: bold; border: 3px dashed white; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Carga de Pedido")
        raw_data = st.text_area("Pegue aquí el pedido:", placeholder="TEJA FLEXIFORTE #5 200\nTEJA #4 150")
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
                if key in line_upper: # Busca "#4", "#5", etc.
                    try:
                        cant = int(parts[-1])
                        completos = cant // data["paquete"]
                        sobra = cant % data["paquete"]
                        
                        peso_material = cant * data["peso"]
                        estibas_linea = completos + (1 if sobra > 0 else 0)
                        
                        peso_total_pedido += peso_material + (estibas_linea * PESO_ESTIBA)
                        total_estibas += estibas_linea
                        
                        pedido_items.append({"id": key, "nombre": data["nombre"], "paq": completos, "sobra": sobra, "largo": data["largo_ft"]})
                    except: pass

    if pedido_items:
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        st.markdown(f"### 🚛 Vehículo Sugerido: {vh['tipo']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total (+Estibas)", f"{peso_total_pedido:,.1f} kg")
        c2.metric("Total Bultos", total_estibas)
        c3.metric("Largo Planchón", f"{vh['largo_planchon_ft']} ft")

        # Preparar bloques (Verdes y Amarillos)
        bloques_totales = []
        pedido_items = sorted(pedido_items, key=lambda x: x["largo"], reverse=True)

        for item in pedido_items:
            for _ in range(item["paq"]):
                bloques_totales.append({"label": f"{item['nombre']}<br>130 UN", "tipo": "verde"})
            if item["sobra"] > 0:
                bloques_totales.append({"label": f"SALDO {item['id']}<br>{item['sobra']} UN", "tipo": "amarillo"})

        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        # Paquete atravesado si es impar
        atravesado = None
        if len(bloques_totales) % 2 != 0:
            atravesado = bloques_totales.pop()

        # Dibujar cuadrícula
        for i in range(0, len(bloques_totales), 2):
            col_izq, col_der = st.columns(2)
            for idx, col in enumerate([col_izq, col_der]):
                bloque = bloques_totales[i + idx]
                clase = "paquete-v" if bloque["tipo"] == "verde" else "saldo-v"
                col.markdown(f'<div class="{clase}">{bloque["label"]}</div>', unsafe_allow_html=True)

        if atravesado:
            clase_h = "paquete-h" if atravesado["tipo"] == "verde" else "saldo-v"
            st.markdown(f'<div class="{clase_h}">📦 CARGA TRASERA (ATRAVESADA)<br>{atravesado["label"]}</div>', unsafe_allow_html=True)
    else:
        st.info("💡 Pegue su pedido en el lateral. Ejemplo: 'TEJA FLEXIFORTE #5 200'")
