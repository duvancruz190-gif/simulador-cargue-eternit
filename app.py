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

if not st.session_state.autenticado:
    # --- LOGIN ---
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
    st.markdown('<div style="background:#E30613; padding:12px; border-radius:8px; text-align:center; color:white; font-weight:bold; font-size:22px; margin-bottom:20px;">🚛 SIMULADOR DE CARGUE - LÓGICA DE SALDOS MÁX 60</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cabina { background:#1A3A5A; color:white; text-align:center; padding:15px; font-weight:bold; border-radius:8px 8px 0 0; }
    .paquete-v { background:#1b5e20; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #0d3b11; min-height: 85px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
    .saldo-box { background:#b7950b; color:white; text-align:center; padding:12px; margin:4px; border-radius:5px; font-weight:bold; border:1px solid #7d6608; min-height: 85px; display: flex; align-items: center; justify-content: center; flex-direction: column; }
    .footer-pies { background: #f0f2f6; padding: 8px; text-align: center; border-radius: 0 0 5px 5px; font-weight: bold; border: 1px solid #d1d3d8; margin-bottom: 10px; color: #1A3A5A; }
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
                        pedido_items.append({"tipo": f"TEJA #{num_ref}", "cant": cant, "peso": cant * info["peso"], "largo": info["largo_ft"], "paquete_nom": info["paquete"]})
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        # --- LÓGICA DE CARRILES CON TOPE DE 60 ---
        carril_izq = []
        carril_der = []
        
        pedido_sorted = sorted(pedido_items, key=lambda x: x['largo'], reverse=True)

        for item in pedido_sorted:
            p_nom = item['paquete_nom']
            num_paquetes = item['cant'] // p_nom
            sobra = item['cant'] % p_nom
            
            # 1. Paquetes verdes completos (Pares)
            for _ in range(num_paquetes // 2):
                bulto = {"label": item["tipo"], "cant": p_nom, "largo": item["largo"], "color": "verde"}
                carril_izq.append(bulto)
                carril_der.append(bulto)
            
            # 2. Manejo de sobrantes (Paquete impar + unidades sueltas)
            unidades_restantes = (p_nom if num_paquetes % 2 != 0 else 0) + sobra
            
            while unidades_restantes > 0:
                # Si el total restante es > 120, sacamos 60 para cada lado
                # Si es < 120, repartimos a la mitad (máximo 60)
                por_lado = min(unidades_restantes // 2, 60)
                if por_lado == 0 and unidades_restantes > 0: por_lado = unidades_restantes # Caso última unidad
                
                mitad = por_lado
                resto = por_lado # Mantenemos simetría
                
                # Para asegurar que no excedemos el total en el último bulto
                if (mitad + resto) > unidades_restantes:
                    mitad = unidades_restantes // 2
                    resto = unidades_restantes - mitad

                carril_izq.append({"label": item["tipo"], "cant": mitad, "largo": item["largo"], "color": "amarillo"})
                carril_der.append({"label": item["tipo"], "cant": resto, "largo": item["largo"], "color": "amarillo"})
                unidades_restantes -= (mitad + resto)
                if unidades_restantes <= 1: unidades_restantes = 0 # Evitar bucles por decimales

        # --- RENDERIZADO ---
        st.divider()
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        col_izq, col_der = st.columns(2)
        
        largo_izq = sum([p['largo'] for p in carril_izq])
        largo_der = sum([p['largo'] for p in carril_der])

        with col_izq:
            for p in carril_izq:
                clase = "paquete-v" if p['color'] == "verde" else "saldo-box"
                st.markdown(f'<div class="{clase}">{p["label"]}<br>({p["cant"]} UND)<br>{p["largo"]} ft</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="footer-pies">Total Izq: {largo_izq} ft</div>', unsafe_allow_html=True)

        with col_der:
            for p in carril_der:
                clase = "paquete-v" if p['color'] == "verde" else "saldo-box"
                st.markdown(f'<div class="{clase}">{p["label"]}<br>({p["cant"]} UND)<br>{p["largo"]} ft</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="footer-pies">Total Der: {largo_der} ft</div>', unsafe_allow_html=True)

        # Alarma de Peso y Espacio
        max_largo = max(largo_izq, largo_der)
        c1, c2 = st.columns(2)
        c1.metric("Peso Total", f"{peso_total_pedido:,.2f} kg")
        c2.metric("Largo Ocupado", f"{max_largo} ft")

        if max_largo > vh['largo_planchon_ft']:
            st.error(f"⚠️ NO CABE EN {vh['tipo']}: Largo excedido.")
