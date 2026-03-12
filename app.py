import streamlit as st
import pandas as pd
import re

# 1. CONFIGURACIÓN Y DATOS TÉCNICOS
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

st.set_page_config(page_title="Smart Picking PRO", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>CONTROL DE CARGUE ETERNIT</h2>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario (Email)").upper()
        clave = st.text_input("Contraseña", type="password")
        if st.button("Ingresar Sistema", use_container_width=True):
            if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    st.markdown("""
    <style>
        .cabina { background: #1A3A5A; color: white; text-align: center; padding: 15px; font-weight: bold; border-radius: 8px; margin-bottom:10px; border-bottom: 5px solid #E30613; }
        .paquete-v { background: #27ae60; color: white; text-align: center; padding: 12px; margin: 4px; border-radius: 5px; font-size: 13px; font-weight: bold; border: 1px solid #1e8449; }
        .saldo-box { background: #f1c40f; color: #2c3e50; text-align: center; padding: 8px; margin: 4px; border-radius: 5px; font-size: 11px; font-weight: 800; border: 1px solid #d4ac0d; }
        .footer-camion { background: #7f8c8d; color: white; text-align: center; padding: 5px; border-radius: 0 0 15px 15px; margin-top: 10px; font-size: 12px; }
        .alerta-espacio { background: #e74c3c; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("📦 Entrada de Pedido")
        raw_data = st.text_area("Pegar lista de tejas:", height=300, placeholder="TEJA #6 500\nTEJA #4 200")
        if st.button("Resetear"):
            st.rerun()

    pedido_items = []
    peso_total_pedido = 0
    
    if raw_data:
        lines = raw_data.strip().split('\n')
        for line in lines:
            line_upper = line.upper().strip()
            if not line_upper: continue
            match_ref = re.search(r'#(\d+)', line_upper)
            if match_ref:
                num_ref = match_ref.group(1)
                if num_ref in PRODUCTOS_BASE:
                    numeros = re.findall(r'\d+', line_upper.replace(f"#{num_ref}", ""))
                    if numeros:
                        cant = int(numeros[-1])
                        info = PRODUCTOS_BASE[num_ref]
                        pedido_items.append({
                            "tipo": f"TEJA #{num_ref}", 
                            "cant": cant, 
                            "peso": cant * info["peso"], 
                            "ref": num_ref,
                            "largo": info["largo_ft"]
                        })
                        peso_total_pedido += cant * info["peso"]

    if pedido_items:
        vh = next((v for v in VEHICULOS if v["capacidad_max"] >= peso_total_pedido), VEHICULOS[-1])
        
        # --- RESUMEN DE CARGA ---
        st.subheader(f"🚛 Plan de Cargue: {vh['tipo']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Peso Total", f"{peso_total_pedido:,.0f} kg")
        c2.metric("Capacidad Vehículo", f"{vh['capacidad_max']} kg")
        c3.metric("Espacio Disponible", f"{vh['largo_planchon_ft']} ft")

        # --- LÓGICA DE DISTRIBUCIÓN POR "PASOS" (PIES) ---
        # Ordenamos de mayor a menor longitud para optimizar el planchón
        pedido_sorted = sorted(pedido_items, key=lambda x: x['largo'], reverse=True)
        
        filas_verdes = []
        bloques_amarillos = []
        MAX_SALDO = 60

        for item in pedido_sorted:
            paq_std = PRODUCTOS_BASE[item['ref']]['paquete']
            n_paquetes = item["cant"] // paq_std
            sobra = item["cant"] % paq_std
            
            # Paquetes completos
            for _ in range(n_paquetes):
                filas_verdes.append({"label": item["tipo"], "cant": paq_std, "largo": item["largo"]})
            
            # Fragmentación de saldos (Máximo 60 por bloque)
            while sobra > 0:
                unidades = MAX_SALDO if sobra > MAX_SALDO else sobra
                bloques_amarillos.append({"label": item["tipo"], "cant": unidades})
                sobra -= unidades

        # --- RENDERIZADO VISUAL ---
        st.markdown('<div class="cabina">FRENTE (CABINA)</div>', unsafe_allow_html=True)
        
        pies_ocupados = 0
        paquetes_aux = list(filas_verdes)
        saldos_aux = list(bloques_amarillos)

        # Agrupamos verdes de a 2 (comparten el mismo "paso" lineal)
        while paquetes_aux:
            row = []
            row.append(paquetes_aux.pop(0))
            if paquetes_aux and paquetes_aux[0]['largo'] == row[0]['largo']:
                row.append(paquetes_aux.pop(0))
            
            pies_ocupados += row[0]['largo']
            
            # Dibujar fila
            cols = st.columns([1, 1.5, 1.5, 1])
            with cols[0]: # Saldo Izq
                if saldos_aux:
                    s = saldos_aux.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
            with cols[1]: # Paquete 1
                st.markdown(f'<div class="paquete-v">{row[0]["label"]}<br>{row[0]["cant"]} UND<br>({row[0]["largo"]} ft)</div>', unsafe_allow_html=True)
            with cols[2]: # Paquete 2 (si existe)
                if len(row) > 1:
                    st.markdown(f'<div class="paquete-v">{row[1]["label"]}<br>{row[1]["cant"]} UND<br>({row[1]["largo"]} ft)</div>', unsafe_allow_html=True)
            with cols[3]: # Saldo Der
                if saldos_aux:
                    s = saldos_aux.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        # Saldos restantes si ya no hay paquetes verdes
        while saldos_aux:
            cols_s = st.columns([1, 1.5, 1.5, 1])
            with cols_s[0]:
                if saldos_aux:
                    s = saldos_aux.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)
            with cols_s[3]:
                if saldos_aux:
                    s = saldos_aux.pop(0)
                    st.markdown(f'<div class="saldo-box">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="footer-camion">LONGITUD TOTAL UTILIZADA: {pies_ocupados} ft de {vh["largo_planchon_ft"]} ft</div>', unsafe_allow_html=True)

        if pies_ocupados > vh["largo_planchon_ft"]:
            st.markdown(f'<div class="alerta-espacio">⚠️ ¡ALERTA! La carga excede el largo del planchón por {pies_ocupados - vh["largo_planchon_ft"]} ft</div>', unsafe_allow_html=True)
    else:
        st.info("Ingrese el pedido en el panel lateral para calcular la distribución.")
