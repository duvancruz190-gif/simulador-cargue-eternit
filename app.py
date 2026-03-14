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

# ==========================================================
# LOGIN
# ==========================================================

if not st.session_state.autenticado:
    st.markdown("""
    <style>
    [data-testid="stHeaderActionElements"] {display:none;}
    div.stButton > button { background-color:#E30613; color:white; border:none; font-weight:bold; padding:12px; font-size:17px; border-radius:8px; }
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        try: st.image("logo-eternit-400x150-1.png", use_container_width=True)
        except: st.error("Logo no encontrado")
        with st.container(border=True):
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            if st.button("Ingresar al Sistema", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else: st.error("Credenciales incorrectas")

# ==========================================================
# SISTEMA PRINCIPAL
# ==========================================================

else:
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - LOGÍSTICA</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; border-bottom:5px solid #bdc3c7; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; }
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
                        nombre = f"FLEX. #{num_ref}" if "FLEXIFORTE" in line_upper else f"TEJA #{num_ref}"
                        pedido_items.append({
                            "tipo": nombre, "cant": cant, "peso": cant * info["peso"], 
                            "ref_num": int(num_ref), "largo_ft": info["largo_ft"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        st.subheader(f"🚛 Vehículo sugerido: {vh['tipo']}")
        
        # --- LÓGICA DE DISTRIBUCIÓN CON REGLAS DE SEGURIDAD ---
        # 1. Ordenar pedido por medida de mayor a menor (Ej: 10, 8, 6, 5, 4)
        pedido_sorted = sorted(pedido_items, key=lambda x: x['ref_num'], reverse=True)

        paquetes_verdes = []
        saldos_naranja = []

        for item in pedido_sorted:
            paq_max = PRODUCTOS_BASE[str(item['ref_num'])]['paquete']
            completos = item["cant"] // paq_max
            sobra = item["cant"] % paq_max

            for _ in range(completos):
                paquetes_verdes.append({"label": item["tipo"], "cant": paq_max, "ref": item["ref_num"], "largo": item["largo_ft"]})

            if sobra > 10:
                m1 = sobra // 2
                m2 = sobra - m1
                saldos_naranja.append({"label": item["tipo"], "cant": m1, "ref": item["ref_num"]})
                saldos_naranja.append({"label": item["tipo"], "cant": m2, "ref": item["ref_num"]})
            elif sobra > 0:
                saldos_naranja.append({"label": item["tipo"], "cant": sobra, "ref": item["ref_num"]})

        # Identificar paquete atravesado (el último de la lista verde si es impar)
        paq_render = list(paquetes_verdes)
        atravesado = paq_render.pop() if len(paq_render) % 2 != 0 else None
        rows = [paq_render[i:i+2] for i in range(0, len(paq_render), 2)]
        
        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

        largo_ocupado = 0
        limite_ft = vh['largo_planchon_ft']

        # Renderizado de filas principales
        for row in rows:
            avance = max([p['largo'] for p in row])
            if largo_ocupado + avance <= limite_ft:
                cols = st.columns([1, 1.5, 1.5, 1])
                with cols[0]:
                    if saldos_naranja:
                        s = saldos_naranja.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
                with cols[1]: st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
                with cols[2]: st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)
                with cols[3]:
                    if saldos_naranja:
                        s = saldos_naranja.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
                largo_ocupado += avance

        # Lógica de Paquete Trasero + Saldos compatibles
        if atravesado:
            if largo_ocupado + atravesado['largo'] <= limite_ft:
                c_final = st.columns([1, 3, 1])
                
                # Regla: El saldo solo va si es <= que la base del atravesado
                with c_final[0]:
                    if saldos_naranja and saldos_naranja[0]['ref'] <= atravesado['ref']:
                        s = saldos_naranja.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
                
                with c_final[1]:
                    st.markdown(f'<div class="paquete-h">📦 PAQUETE TRASERO<br>{atravesado["label"]} ({atravesado["cant"]} UND)</div>', unsafe_allow_html=True)
                
                with c_final[2]:
                    if saldos_naranja and saldos_naranja[0]['ref'] <= atravesado['ref']:
                        s = saldos_naranja.pop(0)
                        st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        # Si sobran saldos que no pudieron ir sobre el atravesado por ser grandes
        if saldos_naranja:
            st.caption("Saldos restantes (deben ir en planchón por dimensiones):")
            st.write(", ".join([f"{s['label']} ({s['cant']})" for s in saldos_naranja]))

    else:
        st.info("Pegue un pedido para iniciar.")
