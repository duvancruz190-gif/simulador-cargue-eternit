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
    # --- INTERFAZ ---
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - LOGÍSTICA</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; font-size:14px; }
    .paquete-h { background:#1b4f72; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:80%; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #7d6608; }
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
                            "ref_num": int(num_ref), "largo": info["largo_ft"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        # 1. Alarma de Peso
        vh_max_cap = VEHICULOS[-1]['capacidad_max']
        if peso_total_pedido > vh_max_cap:
            exceso = peso_total_pedido - vh_max_cap
            st.error(f"❌ EL PEDIDO EXCEDE LA CAPACIDAD MÁXIMA POR {exceso:,.2f} KG")
        
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Vehículo Sugerido", vh['tipo'])
        c3.metric("Largo Planchón", f"{vh['largo_planchon_ft']} ft")

        # --- LÓGICA DE DISTRIBUCIÓN POR COLUMNAS INDEPENDIENTES ---
        paquetes_lista = []
        for item in sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True):
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            completos = item["cant"] // paq_max
            for _ in range(completos):
                paquetes_lista.append({"label": item["tipo"], "cant": paq_max, "ref": item["ref_num"], "largo": item["largo"]})
            
            # Saldos consolidados (max 60)
            sobra = item["cant"] % paq_max
            while sobra > 0:
                unidades = min(sobra, 60)
                paquetes_lista.append({"is_saldo": True, "label": item["tipo"], "cant": unidades, "ref": item["ref_num"], "largo": item["largo"]})
                sobra -= unidades

        col_izq, col_der = [], []
        largo_izq, largo_der = 0, 0
        limite = vh['largo_planchon_ft']
        atrasado = None
        fuera_de_cargue = False

        # Llenado inteligente de columnas
        for p in paquetes_lista:
            # Si es un paquete completo y hay un gran desbalance, tratar de equilibrar
            if largo_izq <= largo_der:
                if largo_izq + p['largo'] <= limite:
                    col_izq.append(p)
                    largo_izq += p['largo']
                else: fuera_de_cargue = True
            else:
                if largo_der + p['largo'] <= limite:
                    col_der.append(p)
                    largo_der += p['largo']
                else: fuera_de_cargue = True

        # Renderizado
        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        # Máximo de filas posibles para dibujar
        max_rows = max(len(col_izq), len(col_der))
        for i in range(max_rows):
            c = st.columns([1, 1, 1, 1])
            with c[1]: # Columna Izquierda
                if i < len(col_izq):
                    p = col_izq[i]
                    clase = "saldo-box" if p.get('is_saldo') else "paquete-v"
                    st.markdown(f'<div class="{clase}">{p["label"]}<br>({p["cant"]})</div>', unsafe_allow_html=True)
            with c[2]: # Columna Derecha
                if i < len(col_der):
                    p = col_der[i]
                    clase = "saldo-box" if p.get('is_saldo') else "paquete-v"
                    st.markdown(f'<div class="{clase}">{p["label"]}<br>({p["cant"]})</div>', unsafe_allow_html=True)

        if fuera_de_cargue:
            st.error("⚠️ ALARMA: NO CABE TODO EL PEDIDO POR LARGO DEL PLANCHÓN.")
        
        st.info(f"Ocupación: Izquierda {largo_izq}ft | Derecha {largo_der}ft")
