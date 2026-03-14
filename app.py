import streamlit as st
import pandas as pd
import re

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Simulador de Cargue Pro", page_icon="🚛", layout="wide")

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
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - BALANCEADO</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; min-height: 90px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #7d6608; }
    .footer-pies { background: #f0f2f6; padding: 5px; text-align: center; border-radius: 0 0 5px 5px; font-weight: bold; border: 1px solid #d1d3d8; margin-bottom: 10px; font-size: 14px; }
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
                            "ref_num": int(num_ref), "largo_ft": info["largo_ft"], "paquete_nom": info["paquete"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        # Selección de vehículo y alertas de peso
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Vehículo Sugerido", vh['tipo'])
        c3.metric("Capacidad Máxima", f"{vh['capacidad_max']:,.0f} kg")

        if peso_total_pedido > VEHICULOS[-1]['capacidad_max']:
            st.error(f"❌ EL PEDIDO EXCEDE LA CAPACIDAD MÁXIMA POR {peso_total_pedido - VEHICULOS[-1]['capacidad_max']:,.2f} KG")

        # --- LÓGICA DE BALANCEO POR CARRILES ---
        carril_izq = []
        carril_der = []
        todos_saldos = []
        
        # Ordenar por largo para estabilidad (las más largas adelante)
        pedido_sorted = sorted(pedido_items, key=lambda x: x['largo_ft'], reverse=True)

        for item in pedido_sorted:
            paq_nom = item['paquete_nom']
            num_paquetes = item['cant'] // paq_nom
            sobrante_unidades = item['cant'] % paq_nom
            
            # Emparejar paquetes verdes (2 en 2)
            while num_paquetes >= 2:
                bulto = {"label": item["tipo"], "cant": paq_nom, "largo": item["largo_ft"]}
                carril_izq.append(bulto)
                carril_der.append(bulto)
                num_paquetes -= 2
            
            # Si queda uno solo (IMPAR), lo partimos para subirlo como saldos
            if num_paquetes == 1:
                mitad = paq_nom // 2
                resto = paq_nom - mitad
                todos_saldos.append({"label": item["tipo"], "cant": mitad})
                todos_saldos.append({"label": item["tipo"], "cant": resto})
            
            # Sumar las unidades sueltas originales a la lista de saldos
            if sobrante_unidades > 0:
                todos_saldos.append({"label": item["tipo"], "cant": sobrante_unidades})

        # --- RENDERIZADO VISUAL ---
        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        col_ext_izq, col_int_izq, col_int_der, col_ext_der = st.columns([1, 2, 2, 1])

        largo_final = sum([p['largo'] for p in carril_izq])

        with col_int_izq:
            for p in carril_izq:
                st.markdown(f'<div class="paquete-v">{p["label"]}<br>({p["cant"]} UND)<br>{p["largo"]} ft</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="footer-pies">{largo_final} ft</div>', unsafe_allow_html=True)

        with col_int_der:
            for p in carril_der:
                st.markdown(f'<div class="paquete-v">{p["label"]}<br>({p["cant"]} UND)<br>{p["largo"]} ft</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="footer-pies">{largo_final} ft</div>', unsafe_allow_html=True)

        # Repartir saldos amarillos a los costados
        with col_ext_izq:
            for i in range(0, len(todos_saldos), 2):
                s = todos_saldos[i]
                st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
        
        with col_ext_der:
            for i in range(1, len(todos_saldos), 2):
                s = todos_saldos[i]
                st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        # Alarma de espacio físico
        if largo_final > vh['largo_planchon_ft']:
            st.error(f"⚠️ NO CABE: El cargue mide {largo_final} ft y el planchón del {vh['tipo']} es de {vh['largo_planchon_ft']} ft.")
        else:
            st.success(f"✅ Cargue balanceado y optimizado para {vh['tipo']}.")
