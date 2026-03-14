import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------

st.set_page_config(
    page_title="Simulador de Cargue",
    page_icon="🚛",
    layout="wide"
)

USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# -----------------------------
# BASE PRODUCTOS
# -----------------------------

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

# -----------------------------
# VEHÍCULOS (Dimensiones Reales)
# -----------------------------

VEHICULOS = [
    {"tipo": "TURBO", "capacidad_max": 5000, "largo_planchon_ft": 16},
    {"tipo": "SENCILLO", "capacidad_max": 10000, "largo_planchon_ft": 20},
    {"tipo": "DOBLE TROQUE", "capacidad_max": 18000, "largo_planchon_ft": 24},
    {"tipo": "CUATRO MANOS", "capacidad_max": 22000, "largo_planchon_ft": 28},
    {"tipo": "MULA", "capacidad_max": 34000, "largo_planchon_ft": 40},
]

# -----------------------------
# ESTADO LOGIN
# -----------------------------

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ==========================================================
# LOGIN
# ==========================================================

if not st.session_state.autenticado:

    st.markdown("""
    <style>
    [data-testid="stHeaderActionElements"] {display:none;}
    div.stButton > button {
        background-color:#E30613;
        color:white;
        border:none;
        font-weight:bold;
        padding:12px;
        font-size:17px;
        border-radius:8px;
    }
    div.stButton > button:hover{
        background-color:#b3050f;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1.4,1])

    with col2:
        st.markdown(
        """
        <h1 style='text-align:center;
        color:#1A3A5A;
        font-weight:800;
        font-size:40px;
        margin-top:10px'>
        Simulador de Cargue
        </h1>
        """,
        unsafe_allow_html=True
        )

        with st.container(border=True):
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")

            if st.button("Ingresar al Sistema", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

# ==========================================================
# SISTEMA
# ==========================================================

else:

    # HEADER
    st.markdown("""
    <div style="
    background:#E30613;
    padding:12px;
    border-radius:8px;
    text-align:center;
    color:white;
    font-weight:bold;
    font-size:22px;
    margin-bottom:20px;
    ">
    🚛 SIMULADOR DE CARGUE - LOGÍSTICA
    </div>
    """, unsafe_allow_html=True)

    # ESTILOS
    st.markdown("""
    <style>
    .cabina {
    background:#1A3A5A;
    color:white;
    text-align:center;
    padding:15px;
    font-weight:bold;
    border-radius:8px 8px 0 0;
    border-bottom:5px solid #bdc3c7;
    }
    .paquete-v{
    background:#27ae60;
    color:white;
    text-align:center;
    padding:12px;
    margin:4px;
    border-radius:5px;
    font-weight:bold;
    border:1px solid #1e8449;
    }
    .saldo-box{
    background:#f1c40f;
    color:#2c3e50;
    text-align:center;
    padding:8px;
    margin:4px;
    border-radius:5px;
    font-size:11px;
    font-weight:800;
    border:1px solid #d4ac0d;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

    with st.sidebar:
        st.header("📋 Pedido")
        raw_data = st.text_area(
            "Pegue el pedido aquí",
            height=300,
            placeholder="Ejemplo:\nTEJA FLEXIFORTE #5 900\nTEJA PERFIL #4 150"
        )
        if st.button("Limpiar"):
            st.rerun()

# ==========================================================
# PROCESAMIENTO PEDIDO
# ==========================================================

    pedido_items = []
    peso_total_pedido = 0

    if raw_data:
        lines = raw_data.strip().split("\n")
        for line in lines:
            line_upper = line.upper().strip()
            match_ref = re.search(r'#(\d+)', line_upper)
            if match_ref:
                num_ref = match_ref.group(1)
                if num_ref in PRODUCTOS_BASE:
                    numeros = re.findall(r'\d+', line_upper.replace(f"#{num_ref}", ""))
                    if numeros:
                        cant = int(numeros[-1])
                        info = PRODUCTOS_BASE[num_ref]
                        nombre = f"FLEX. #{num_ref}" if "FLEXIFORTE" in line_upper else f"TEJA #{num_ref}"
                        pedido_items.append({
                            "tipo": nombre,
                            "cant": cant,
                            "peso": cant * info["peso"],
                            "ref": num_ref
                        })
                        peso_total_pedido += cant * info["peso"]

# ==========================================================
# LÓGICA DE DISTRIBUCIÓN ESTRICTA
# ==========================================================

    if pedido_items:
        # Selección inicial del vehículo (por peso y largo máximo del material)
        largo_req_max = max([PRODUCTOS_BASE[i['ref']]['largo_ft'] for i in pedido_items])
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido and v["largo_planchon_ft"] >= largo_req_max), VEHICULOS[-1])

        st.subheader(f"🚛 Vehículo sugerido: {vh['tipo']}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Capacidad Máx", f"{vh['capacidad_max']:,.0f} kg")
        c3.metric("Planchón Vehículo", f"{vh['largo_planchon_ft']} ft")

        # --- Algoritmo de acomodación ---
        espacio_disponible = vh["largo_planchon_ft"]
        paquetes_planchon = []
        saldos_segundo_nivel = []
        no_cabe_material = False

        # Ordenar de mayor a menor largo
        pedido_sorted = sorted(pedido_items, key=lambda x: int(x['ref']), reverse=True)

        for item in pedido_sorted:
            largo_ft = PRODUCTOS_BASE[item['ref']]['largo_ft']
            paq_max = PRODUCTOS_BASE[item['ref']]['paquete']
            
            cant_actual = item["cant"]
            
            # Ubicar paquetes completos en planchón
            while cant_actual >= paq_max:
                if espacio_disponible >= largo_ft:
                    paquetes_planchon.append({"label": item["tipo"], "cant": paq_max, "ref": item["ref"]})
                    # Restamos del largo cada 2 paquetes (izquierda y derecha)
                    if len(paquetes_planchon) % 2 == 0:
                        espacio_disponible -= largo_ft
                    cant_actual -= paq_max
                else:
                    no_cabe_material = True
                    break
            
            # Si quedó un paquete solo al final de la tanda, resta su largo
            if len(paquetes_planchon) % 2 != 0 and cant_actual < paq_max:
                pass # El ajuste de resta se hace al final o al cambiar de referencia

            # Ubicar saldos en segundo nivel (max 60 por estiba)
            while cant_actual > 0:
                unidades = min(cant_actual, 60)
                saldos_segundo_nivel.append({"label": item["tipo"], "cant": unidades})
                cant_actual -= unidades

        # Ajuste final de espacio si el último paquete quedó sin pareja
        # (Ocupa el largo aunque esté solo a un lado)
        total_longitud_ocupada = 0
        temp_list = paquetes_planchon.copy()
        while temp_list:
            p1 = temp_list.pop(0)
            total_longitud_ocupada += PRODUCTOS_BASE[p1['ref']]['largo_ft']
            if temp_list: # Si hay pareja
                temp_list.pop(0) 
        
        espacio_restante_final = vh["largo_planchon_ft"] - total_longitud_ocupada

        st.divider()

        if no_cabe_material or espacio_restante_final < 0:
            st.error(f"❌ EL MATERIAL NO CABE: Se ha agotado el largo del planchón ({vh['largo_planchon_ft']}ft).")
        else:
            st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

            # Renderizar Piso 1 (Planchón)
            filas_p1 = [paquetes_planchon[i:i+2] for i in range(0, len(paquetes_planchon), 2)]
            for fila in filas_p1:
                cols = st.columns([1,1.5,1.5,1])
                with cols[1]:
                    st.markdown(f'<div class="paquete-v">{fila[0]["label"]}<br>({fila[0]["cant"]})</div>', unsafe_allow_html=True)
                with cols[2]:
                    if len(fila) > 1:
                        st.markdown(f'<div class="paquete-v">{fila[1]["label"]}<br>({fila[1]["cant"]})</div>', unsafe_allow_html=True)

            # Renderizar Segundo Nivel (Saldos)
            if saldos_segundo_nivel:
                st.markdown("### 📦 Segundo Nivel (Saldos sobre estibas - Máx 60 und)")
                filas_s = [saldos_segundo_nivel[i:i+4] for i in range(0, len(saldos_segundo_nivel), 4)]
                for fs in filas_s:
                    cols_s = st.columns(4)
                    for i, s in enumerate(fs):
                        with cols_s[i]:
                            st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

            st.info(f"Espacio restante en planchón: {espacio_restante_final} pies.")

    else:
        st.info("Pegue un pedido en el panel izquierdo para generar la simulación.")
