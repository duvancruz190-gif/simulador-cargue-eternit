import streamlit as st

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

PRODUCTOS = {
    "TEJA #4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "TEJA #5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "TEJA #6": {"peso": 17.72, "paquete": 17.72, "largo_ft": 6},
    "TEJA #8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "TEJA #10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

PESO_ESTIBA = 30 # kg por cada paquete o saldo grande

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

st.set_page_config(page_title="Smart Picking & Logistic Guide", layout="wide")

# --- FUNCIÓN DE LOGIN ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                st.image("ETERNIT LOGOS.webp", use_container_width=True)
            except:
                st.markdown("<h1 style='text-align:center;'>ETERNIT</h1>", unsafe_allow_html=True)
            
            st.subheader("Inicie sesión para continuar")
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
        return False
    return True

if login():
    # 2. ESTILOS CSS
    st.markdown("""
    <style>
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 15px; font-weight: bold; border-radius: 10px 10px 0 0; margin-bottom: 10px; }
        .celda-verde { background: #27ae60; color: white; text-align: center; padding: 12px; margin: 4px; border-radius: 6px; font-weight: bold; min-height: 60px; font-size: 0.8rem; }
        .celda-amarilla { background: #f1c40f; color: black; text-align: center; padding: 12px; margin: 4px; border-radius: 6px; font-weight: bold; min-height: 60px; font-size: 0.8rem; border: 2px solid #d4ac0d; }
        .vacio { height: 60px; margin: 4px; }
        .paquete-h { background: #2980b9; color: white; text-align: center; padding: 20px; margin: 10px 4px; border-radius: 8px; font-weight: bold; border: 3px dashed white; }
    </style>
    """, unsafe_allow_html=True)

    # 3. SIDEBAR / ENTRADA EXCEL
    with st.sidebar:
        st.header("📦 Carga de Pedido")
        raw_data = st.text_area("Pegue el pedido (Nombre y Cantidad):", height=200, placeholder="Ejemplo:\nTEJA #4 260\nTEJA #6 50")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

    # 4. PROCESAMIENTO DE LÓGICA
    pedido_items = []
    peso_total_material = 0
    conteo_estibas = 0

    if raw_data:
        lines = raw_data.strip().split('\n')
        for line in lines:
            for key, data in PRODUCTOS.items():
                if key in line.upper():
                    try:
                        cant = int(line.split()[-1])
                        completos = cant // data["paquete"]
                        sobra = cant % data["paquete"]
                        
                        peso_item = cant * data["peso"]
                        peso_total_material += peso_item
                        
                        # Cada paquete y cada saldo cuenta como una estiba física
                        estibas_item = completos + (1 if sobra > 0 else 0)
                        conteo_estibas += estibas_item
                        
                        pedido_items.append({
                            "nombre": key, "cant": cant, "paq": completos, "saldo": sobra, "largo": data["largo_ft"]
                        })
                    except: pass

    if pedido_items:
        peso_final = peso_total_material + (conteo_estibas * PESO_ESTIBA)
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_final), VEHICULOS[-1])

        # MÉTRICAS
        st.markdown(f"### 🚛 Análisis de Distribución: {vh['tipo']}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Peso Total (inc. estibas)", f"{peso_final:,.0f} kg")
        m2.metric("Capacidad Libre", f"{vh['capacidad_max'] - peso_final:,.0f} kg")
        m3.metric("Total Estibas/Paquetes", conteo_estibas)
        m4.metric("Largo Vehículo", f"{vh['largo_planchon_ft']} ft")

        # ORGANIZAR CARGA (Verticales y Saldos)
        carga_vertical = [] # Los verdes
        carga_saldos = []   # Los amarillos
        
        # Ordenar por largo para balanceo
        pedido_items = sorted(pedido_items, key=lambda x: x["largo"], reverse=True)

        for item in pedido_items:
            for _ in range(item["paq"]):
                carga_vertical.append(f"{item['nombre']}<br>130 UN")
            if item["saldo"] > 0:
                carga_saldos.append(f"SALDO {item['nombre']}<br>{item['saldo']} UN")

        # 5. MAPA VISUAL
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        # Unir ambas listas para llenar el camión
        total_bloques = carga_vertical + carga_saldos
        
        # Detectar si hay un paquete que deba ir atravesado (impar)
        bloque_atravesado = None
        if len(total_bloques) % 2 != 0:
            bloque_atravesado = total_bloques.pop()

        # Filas de 2 columnas
        for i in range(0, len(total_bloques), 2):
