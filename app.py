import streamlit as st
import pandas as pd
import re
import math

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
# BASE PRODUCTOS (Pesos reales y paquete #10 corregido)
# -----------------------------

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130, "largo_ft": 4},
    "5": {"peso": 14.77, "paquete": 130, "largo_ft": 5},
    "6": {"peso": 17.72, "paquete": 130, "largo_ft": 6},
    "8": {"peso": 23.63, "paquete": 130, "largo_ft": 8},
    "10": {"peso": 29.54, "paquete": 100, "largo_ft": 10},
}

# -----------------------------
# VEHÍCULOS (Ordenados de menor a mayor)
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
        st.image("logo-eternit-400x150-1.png", use_container_width=True)
        st.markdown("<h1 style='text-align:center;color:#1A3A5A;font-weight:800;font-size:40px;margin-top:10px'>Simulador de Cargue</h1>", unsafe_allow_html=True)
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
    <div style="background:#E30613;padding:12px;border-radius:8px;text-align:center;color:white;font-weight:bold;font-size:22px;margin-bottom:20px;">
    🚛 SIMULADOR DE CARGUE - LOGÍSTICA
    </div>
    """, unsafe_allow_html=True)

    # ESTILOS
    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; border-bottom:5px solid #bdc3c7; }
    .paquete-v{ background:#27ae60; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #1e8449; }
    .paquete-h{ background:#2980b9; color:white; text-align:center; padding:15px; margin:10px auto; border-radius:6px; font-weight:bold; border:2px dashed #ecf0f1; width:80%; }
    .saldo-box{ background:#f1c40f; color:#2c3e50; text-align:center; padding:8px; margin:4px; border-radius:5px; font-size:11px; font-weight:800; border:1px solid #d4ac0d; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

    with st.sidebar:
        st.header("📋 Pedido")
        raw_data = st.text_area("Pegue el pedido aquí", height=300, placeholder="Ejemplo:\nTEJA FLEXIFORTE #5 900")
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
                            "tipo": nombre, "cant": cant, "peso": cant * info["peso"], "ref": num_ref
                        })
                        peso_total_pedido += cant * info["peso"]

# ==========================================================
# RESULTADOS (NUEVA LÓGICA DE CARGUE)
# ==========================================================

    if pedido_items:
        # 1. Identificar referencia principal para calcular espacio
        ref_p = pedido_items[0]["ref"]
        largo_teja = PRODUCTOS_BASE[ref_p]["largo_ft"]
        paq_size = PRODUCTOS_BASE[ref_p]["paquete"]
        paquetes_totales = math.ceil(sum(i['cant'] for i in pedido_items) / paq_size)

        # 2. Buscar el mejor vehículo por peso Y por pasos
        vh_elegido = None
        detalles_cargue = {}

        for v in VEHICULOS:
            # Cálculo de pasos
            paq_por_lado = v["largo_planchon_ft"] // largo_teja
            paq_planchon = paq_por_lado * 2
            sobrante = v["largo_planchon_ft"] - (paq_por_lado * largo_teja)
            atravesado = 1 if sobrante >= 4 else 0
            capacidad_espacio = paq_planchon + atravesado

            if peso_total_pedido <= v["capacidad_max"] and paquetes_totales <= capacidad_espacio:
                vh_elegido = v
                detalles_cargue = {
                    "paq_lado": paq_por_lado,
                    "paq_planchon": paq_planchon,
                    "atravesado": atravesado,
                    "sobrante": sobrante,
                    "capacidad_total": capacidad_espacio
                }
                break
        
        # Si no encontró uno que quepa, usa el más grande (Mula)
        if not vh_elegido:
            vh_elegido = VEHICULOS[-1]
            # Recalcular para la mula
            paq_por_lado = vh_elegido["largo_planchon_ft"] // largo_teja
            detalles_cargue = {
                "paq_lado": paq_por_lado,
                "paq_planchon": paq_por_lado * 2,
                "atravesado": 1 if (vh_elegido["largo_planchon_ft"] % largo_teja) >= 4 else 0,
                "sobrante": vh_elegido["largo_planchon_ft"] % largo_teja,
                "capacidad_total": (paq_por_lado * 2) + (1 if (vh_elegido["largo_planchon_ft"] % largo_teja) >= 4 else 0)
            }

        # MOSTRAR MÉTRICAS
        st.subheader(f"🚛 Vehículo sugerido: {vh_elegido['tipo']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Ocupación Peso", f"{(peso_total_pedido/vh_elegido['capacidad_max']*100):.1f}%")
        c3.metric("Paquetes Lado", detalles_cargue["paq_lado"])
        c4.metric("Espacio Total", f"{detalles_cargue['capacidad_total']} Paq")

        # INDICADOR TMS
        ocupacion = (peso_total_pedido / vh_elegido["capacidad_max"]) * 100
        color = "#27ae60" if ocupacion <= 90 else "#e74c3c"
        if ocupacion < 60: color = "#f1c40f"
        
        st.markdown(f'<div style="background:{color};color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;">UTILIZACIÓN: {ocupacion:.1f}%</div>', unsafe_allow_html=True)
        
        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

# ==========================================================
# LÓGICA DISTRIBUCIÓN (Visualización de los paquetes)
# ==========================================================

        # Creamos la lista de paquetes para dibujar
        mapa_vertical = []
        for item in pedido_items:
            paq = PRODUCTOS_BASE[item['ref']]['paquete']
            completos = item["cant"] // paq
            for _ in range(completos):
                mapa_vertical.append({"label": item["tipo"], "cant": paq})
        
        # Separar el atravesado si la lógica dice que hay uno y el pedido lo requiere
        tiene_atravesado_fisico = False
        paq_para_filas = list(mapa_vertical)
        
        if detalles_cargue["atravesado"] > 0 and len(paq_para_filas) > detalles_cargue["paq_planchon"]:
            paquete_atras = paq_para_filas.pop()
            tiene_atravesado_fisico = True

        rows = [paq_para_filas[i:i+2] for i in range(0, len(paq_para_filas), 2)]

        for row in rows:
            cols = st.columns([1,1.5,1.5,1])
            with cols[1]:
                st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)
            with cols[2]:
                if len(row) > 1:
                    st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)

        if tiene_atravesado_fisico:
            st.markdown(f'<div class="paquete-h">📦 PAQUETE ATRAVESADO (ESPACIO SOBRANTE {detalles_cargue["sobrante"]}ft)<br>{paquete_atras["label"]} ({paquete_atras["cant"]} UND)</div>', unsafe_allow_html=True)

    else:
        st.info("Pegue un pedido en el panel izquierdo para generar la simulación.")
