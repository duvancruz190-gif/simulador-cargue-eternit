# ... (Mantenemos igual hasta la sección de ESTILOS)

# ==========================================================
# ESTILOS MEJORADOS (INGENIERÍA)
# ==========================================================

# Definición de colores por Referencia para Ingeniería
# Usamos tonos: Azul Marino, Gris Acero, Verde Bosque, Petróleo y Carbón
COLORES_REF = {
    "4": "#34495e", # Charcoal
    "5": "#2c3e50", # Navy Deep
    "6": "#2980b9", # Steel Blue
    "8": "#16a085", # Deep Teal
    "10": "#27ae60" # Forest Green
}

st.markdown(f"""
<style>
    .cabina {{
        background:#1A3A5A;
        color:white;
        text-align:center;
        padding:15px;
        font-weight:bold;
        border-radius:8px 8px 0 0;
        border-bottom:5px solid #bdc3c7;
        letter-spacing: 2px;
    }}

    /* Estilo base para paquetes */
    .paquete-v {{
        color:white;
        text-align:center;
        padding:12px;
        margin:4px;
        border-radius:4px;
        font-weight:bold;
        font-size: 14px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }}

    .paquete-h {{
        background:#455a64;
        color:white;
        text-align:center;
        padding:15px;
        margin:10px auto;
        border-radius:6px;
        font-weight:bold;
        border:2px dashed #ecf0f1;
        width:80%;
    }}

    .saldo-box {{
        background:#f8f9fa;
        color:#2c3e50;
        text-align:center;
        padding:8px;
        margin:4px;
        border-radius:4px;
        font-size:11px;
        font-weight:800;
        border:1px solid #dee2e6;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }}
</style>
""", unsafe_allow_html=True)

# ... (Mantenemos igual la sección de SIDEBAR y PROCESAMIENTO)

# ==========================================================
# LÓGICA DISTRIBUCIÓN (MODIFICADA PARA COLORES)
# ==========================================================

    # ... (Dentro del bloque 'if pedido_items:')
    
    mapa_vertical = []
    saldos = []

    for item in pedido_sorted:
        paq = PRODUCTOS_BASE[item['ref']]['paquete']
        
        # Obtenemos el color según la referencia
        color_ref = COLORES_REF.get(item['ref'], "#7f8c8d")

        completos = item["cant"] // paq
        sobra = item["cant"] % paq

        for _ in range(completos):
            mapa_vertical.append({
                "label": item["tipo"], 
                "cant": paq, 
                "color": color_ref # Guardamos el color
            })

        while sobra > 0:
            cant_s = min(sobra, 60)
            saldos.append({
                "label": item["tipo"], 
                "cant": cant_s,
                "color": color_ref
            })
            sobra -= cant_s

    paq_render = list(mapa_vertical)
    atravesado = paq_render.pop() if len(paq_render) % 2 != 0 else None
    rows = [paq_render[i:i+2] for i in range(0, len(paq_render), 2)]
    saldos_render = list(saldos)

    for row in rows:
        cols = st.columns([1,1.5,1.5,1])

        with cols[0]:
            if saldos_render:
                s = saldos_render.pop(0)
                st.markdown(f'<div class="saldo-box" style="border-left: 5px solid {s["color"]}">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

        with cols[1]:
            # Aplicamos el color dinámico aquí
            st.markdown(f'<div class="paquete-v" style="background-color:{row[0]["color"]}">{row[0]["label"]}<br>({row[0]["cant"]})</div>', unsafe_allow_html=True)

        with cols[2]:
            if len(row) > 1:
                # Aplicamos el color dinámico aquí
                st.markdown(f'<div class="paquete-v" style="background-color:{row[1]["color"]}">{row[1]["label"]}<br>({row[1]["cant"]})</div>', unsafe_allow_html=True)

        with cols[3]:
            if saldos_render:
                s = saldos_render.pop(0)
                st.markdown(f'<div class="saldo-box" style="border-right: 5px solid {s["color"]}">{s["label"]}<br>{s["cant"]} UND</div>', unsafe_allow_html=True)

    if atravesado:
        st.markdown(
            f'<div class="paquete-h" style="background-color:{atravesado["color"]}">📦 PAQUETE COMPLETO TRASERO<br>{atravesado["label"]} ({atravesado["cant"]} UND)</div>',
            unsafe_allow_html=True
        )
