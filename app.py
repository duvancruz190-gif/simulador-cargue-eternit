import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue Eternit", page_icon="🚛", layout="wide")

USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

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

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# ==========================================================
# LOGIN
# ==========================================================
if not st.session_state.autenticado:
    st.markdown("<style>div.stButton > button { background-color:#E30613; color:white; font-weight:bold; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        try: st.image("logo-eternit-400x150-1.png", use_container_width=True)
        except: st.warning("Logo Eternit")
        with st.container(border=True):
            usuario = st.text_input("Usuario").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("INGRESAR", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Acceso denegado")
else:
    # ==========================================================
    # SISTEMA DE CARGUE
    # ==========================================================
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - OPTIMIZACIÓN DE PLANCHÓN</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; margin-bottom:10px; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:10px; margin:2px; border-radius:4px; font-weight:bold; border:1px solid #0d3b11; font-size:13px; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:10px; margin:2px; border-radius:4px; font-size:13px; font-weight:bold; border:1px solid #7d6608; }
    .stats-box { background:#f8f9fa; border:1px solid #dee2e6; padding:10px; border-radius:5px; text-align:center; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Entrada de Pedido")
        raw_data = st.text_area("Pegue el pedido aquí", height=250, placeholder="TEJA #10 560...")
        if st.button("Limpiar Pantalla"): st.rerun()

    pedido_items = []
    peso_total_pedido = 0

    if raw_data:
        lines = raw_data.strip().split("\n")
        for line in lines:
            line_upper = line.upper().strip()
            match_ref = re.search(r'#(\d+)', line_upper)
            if match_ref:
                ref = match_ref.group(1)
                if ref in PRODUCTOS_BASE:
                    nums = re.findall(r'\d+', line_upper.replace(f"#{ref}", ""))
                    if nums:
                        cant = int(nums[-1])
                        info = PRODUCTOS_BASE[ref]
                        pedido_items.append({
                            "tipo": f"TEJA #{ref}", "cant": cant, "peso": cant * info["peso"], 
                            "ref_num": int(ref), "largo": info["largo_ft"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        # --- ALERTAS DE CAPACIDAD ---
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        if peso_total_pedido > VEHICULOS[-1]['capacidad_max']:
            st.error(f"⚠️ EXCESO DE PESO: El pedido pesa {peso_total_pedido:,.0f}kg (Excede la Mula por {peso_total_pedido - 34000:,.0f}kg)")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("PESO TOTAL", f"{peso_total_pedido:,.0f} kg")
        c2.metric("VEHÍCULO", vh['tipo'])
        c3.metric("LIMITE PLANCHÓN", f"{vh['largo_planchon_ft']} ft")

        # --- LÓGICA DE TETRIS (COLUMNAS INDEPENDIENTES) ---
        # Creamos una lista plana de "bultos" a cargar, ordenados por tamaño
        inventario_carga = []
        for item in sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True):
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            # Paquetes completos
            for _ in range(item["cant"] // paq_max):
                inventario_carga.append({"label": item["tipo"], "cant": paq_max, "ref": item["ref_num"], "largo": item["largo"], "es_paquete": True})
            # Saldos (máximo 60 por saldo)
            sobra = item["cant"] % paq_max
            while sobra > 0:
                uni = min(sobra, 60)
                inventario_carga.append({"label": item["tipo"], "cant": uni, "ref": item["ref_num"], "largo": item["largo"], "es_paquete": False})
                sobra -= uni

        col_izq, col_der = [], []
        largo_izq, largo_der = 0, 0
        limite = vh['largo_planchon_ft']
        no_cupieron = []

        for bulto in inventario_carga:
            # Intentar meter en la columna que tenga más espacio libre (menor largo ocupado)
            if largo_izq <= largo_der:
                if largo_izq + bulto['largo'] <= limite:
                    col_izq.append(bulto)
                    largo_izq += bulto['largo']
                elif largo_der + bulto['largo'] <= limite: # Si en la izq no cupo, probar en la der
                    col_der.append(bulto)
                    largo_der += bulto['largo']
                else:
                    no_cupieron.append(bulto)
            else:
                if largo_der + bulto['largo'] <= limite:
                    col_der.append(bulto)
                    largo_der += bulto['largo']
                elif largo_izq + bulto['largo'] <= limite:
                    col_izq.append(bulto)
                    largo_izq += bulto['largo']
                else:
                    no_cupieron.append(bulto)

        # --- DIBUJO DEL PLANCHÓN ---
        st.markdown('<div class="cabina">FRONTAL - CABINA DEL VEHÍCULO</div>', unsafe_allow_html=True)
        
        max_filas = max(len(col_izq), len(col_der))
        
        for i in range(max_filas):
            c = st.columns([1, 2, 2, 1])
            with c[1]: # Lado Izquierdo
                if i < len(col_izq):
                    b = col_izq[i]
                    estilo = "paquete-v" if b['es_paquete'] else "saldo-box"
                    st.markdown(f'<div class="{estilo}">{b["label"]}<br>({b["cant"]} UND) - {b["largo"]}ft</div>', unsafe_allow_html=True)
            with c[2]: # Lado Derecho
                if i < len(col_der):
                    b = col_der[i]
                    estilo = "paquete-v" if b['es_paquete'] else "saldo-box"
                    st.markdown(f'<div class="{estilo}">{b["label"]}<br>({b["cant"]} UND) - {b["largo"]}ft</div>', unsafe_allow_html=True)

        # --- ALERTAS FINALES ---
        st.markdown(f"""
        <div style="display: flex; justify-content: space-around; margin-top: 20px;">
            <div class="stats-box"><b>PASOS IZQUIERDA:</b><br>{largo_izq} / {limite} ft</div>
            <div class="stats-box"><b>PASOS DERECHA:</b><br>{largo_der} / {limite} ft</div>
        </div>
        """, unsafe_allow_html=True)

        if no_cupieron:
            st.error(f"❌ ATENCIÓN: No caben {len(no_cupieron)} bultos en este vehículo por falta de espacio en el planchón.")
            with st.expander("Ver bultos que se quedaron por fuera"):
                for nc in no_cupieron:
                    st.write(f"• {nc['label']} ({nc['cant']} UND) - Largo: {nc['largo']}ft")
        else:
            st.success("✅ ¡TODO EL PEDIDO CABE PERFECTAMENTE!")

    else:
        st.info("Esperando datos del pedido para calcular distribución...")
