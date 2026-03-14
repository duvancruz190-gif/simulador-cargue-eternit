import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue", page_icon="🚛", layout="wide")

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

# --- LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<style>div.stButton > button { background-color:#E30613; color:white; font-weight:bold; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        try: st.image("logo-eternit-400x150-1.png", use_container_width=True)
        except: st.warning("Logo no encontrado")
        with st.container(border=True):
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar al Sistema", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Credenciales incorrectas")
else:
    # --- INTERFAZ PRINCIPAL ---
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - LOGÍSTICA</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; }
    .paquete-h { background:#1b4f72; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:80%; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #7d6608; }
    .remonte-box { background:#2874A6; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #1a5276; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📋 Pedido")
        raw_data = st.text_area("Pegue el pedido aquí", height=300)
        if st.button("Limpiar"): st.rerun()

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
                        pedido_items.append({
                            "tipo": f"TEJA #{num_ref}", "cant": cant, "peso": cant * info["peso"], 
                            "ref_num": int(num_ref), "largo_ft": info["largo_ft"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        # Selección de vehículo
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        limite_ft = vh['largo_planchon_ft']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Vehículo Sugerido", vh['tipo'])
        c3.metric("Capacidad Máxima", f"{vh['capacidad_max']:,.0f} kg")

        # --- PROCESAMIENTO DE CARGA ---
        pedido_sorted = sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True)
        paquetes_verdes = []
        saldos_naranja = []

        for item in pedido_sorted:
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            completos = item["cant"] // paq_max
            sobra = item["cant"] % paq_max
            for _ in range(completos):
                paquetes_verdes.append({"label": item["tipo"], "cant": paq_max, "ref": item["ref_num"], "largo": item["largo_ft"]})
            while sobra > 0:
                unidades = min(sobra, 60)
                saldos_naranja.append({"label": item["tipo"], "cant": unidades, "ref": item["ref_num"], "largo": item["largo_ft"]})
                sobra -= unidades

        paq_render = list(paquetes_verdes)
        rows = [paq_render[i:i+2] for i in range(0, len(paq_render), 2)]
        saldos_render = list(saldos_naranja)

        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        largo_centro = 0
        
        # Dibujar filas
        for row in rows:
            avance = max([p['largo'] for p in row])
            largo_centro += avance
            cols = st.columns([1, 1.5, 1.5, 1])
            
            with cols[0]: # Lateral Izquierdo
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND<br>({s["largo"]} ft)</div>', unsafe_allow_html=True)
            
            with cols[1]: st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]: st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)
            
            with cols[3]: # Lateral Derecho
                if saldos_render:
                    s = saldos_render.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND<br>({s["largo"]} ft)</div>', unsafe_allow_html=True)

        # Manejo de paquetes atravesados o sobrantes en el centro
        if len(paq_render) % 2 != 0:
            # Lógica para cuando queda uno solo al final del centro
            p_final = paq_render[-1]
            cols_f = st.columns([1, 3, 1])
            with cols_f[1]: st.markdown(f'<div class="paquete-h">📦 PAQUETE CENTRAL TRASERO<br>{p_final["label"]} ({p_final["cant"]} UND)</div>', unsafe_allow_html=True)

        # SECCIÓN DE REMONTE (MATERIAL QUE VA ARRIBA)
        if saldos_render:
            st.markdown("---")
            st.subheader("📦 MATERIAL EN REMONTE / CARGA SUPERIOR")
            st.info("Este material se distribuye sobre los laterales o encima de los paquetes base.")
            cols_rem = st.columns(5)
            for i, s in enumerate(saldos_render):
                with cols_rem[i % 5]:
                    st.markdown(f'<div class="remonte-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        # MÉTRICAS DE VALIDACIÓN
        st.markdown("---")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Espacio Lineal Ocupado (Piso)", f"{largo_centro} ft", f"{limite_ft - largo_centro} ft libres")
        
        if largo_centro <= limite_ft:
            st.success(f"✅ CARGUE VÁLIDO: El pedido cabe en los {limite_ft} ft del vehículo.")
        else:
            st.error(f"⚠️ ALERTA: El largo total ({largo_centro} ft) supera el planchón del vehículo.")
