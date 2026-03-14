import streamlit as st
import re
import plotly.graph_objects as go

# -----------------------------
# Configuración
# -----------------------------
st.set_page_config(
    page_title="Simulador de Cargue 2D - Camión",
    page_icon="🚛",
    layout="wide"
)

# Datos productos
PRODUCTOS_BASE = {
    "10": {"peso":29.54, "paquete":130}
}

# Vehículos
VEHICULOS = [
    {"tipo":"SENCILLO", "capacidad":10000, "largo":20, "ancho":5, "cabina":4}
]

# -----------------------------
# Sidebar para pedido
# -----------------------------
with st.sidebar:
    st.header("Pedido")
    raw = st.text_area("Pegue el pedido", height=200, placeholder="Ejemplo:\nTEJA #10 500")

# -----------------------------
# Procesar pedido
# -----------------------------
pedido_items = []
if raw:
    lines = raw.strip().split("\n")
    for line in lines:
        line_upper = line.upper().strip()
        match_ref = re.search(r"#(\d+)", line_upper)
        if match_ref:
            num_ref = match_ref.group(1)
            numeros = re.findall(r'\d+', line_upper.replace(f"#{num_ref}",""))
            if numeros:
                cant = int(numeros[-1])
                pedido_items.append({"ref":num_ref, "cantidad":cant})

# -----------------------------
# Dibujar camión con tejas
# -----------------------------
if pedido_items:
    vh = VEHICULOS[0]
    fig = go.Figure()

    # Dibujar cabina
    fig.add_shape(type="rect", x0=0, y0=0, x1=vh["cabina"], y1=vh["ancho"],
                  fillcolor="blue", line=dict(color="black", width=2))
    
    # Dibujar planchón
    fig.add_shape(type="rect", x0=vh["cabina"], y0=0, x1=vh["largo"], y1=vh["ancho"],
                  fillcolor="lightgray", line=dict(color="black", width=2))

    # Preparar filas y columnas
    fila = 0
    columna = 0
    unit_x = 3   # largo de cada paquete
    unit_y = 1   # ancho de cada paquete
    max_col = int((vh["largo"] - vh["cabina"]) // unit_x)
    max_row = int(vh["ancho"] // unit_y)

    # Crear lista de paquetes y saldos
    paquetes = []
    saldos = []

    for item in pedido_items:
        cant_total = item["cantidad"]
        paq_size = PRODUCTOS_BASE[item["ref"]]["paquete"]
        completos = cant_total // paq_size
        sobrante = cant_total % paq_size
        for _ in range(completos):
            paquetes.append(item)
        if sobrante > 0:
            saldos.append({"ref":item["ref"], "cantidad":sobrante})

    # Dibujar filas con saldos a los lados
    for i in range(max_row):
        if i < len(paquetes):
            # Saldo izquierda
            if i < len(saldos):
                s = saldos[i]
                fig.add_shape(type="rect", x0=vh["cabina"], y0=i*unit_y,
                              x1=vh["cabina"]+unit_x, y1=(i+1)*unit_y,
                              fillcolor="yellow", line=dict(color="black"))
                fig.add_annotation(x=vh["cabina"]+unit_x/2, y=i*unit_y+0.5,
                                   text=f"SALDO #{s['ref']} DE {s['cantidad']} UNIDADES",
                                   showarrow=False, font=dict(size=8), textangle=0)
            # Paquete central
            p = paquetes[i]
            fig.add_shape(type="rect", x0=vh["cabina"]+unit_x, y0=i*unit_y,
                          x1=vh["cabina"]+2*unit_x, y1=(i+1)*unit_y,
                          fillcolor="red", line=dict(color="black"))
            fig.add_annotation(x=vh["cabina"]+1.5*unit_x, y=i*unit_y+0.5,
                               text=f"TEJA#{p['ref']}", showarrow=False, font=dict(size=10))
            # Saldo derecha
            if i < len(saldos):
                s = saldos[i]
                fig.add_shape(type="rect", x0=vh["cabina"]+2*unit_x, y0=i*unit_y,
                              x1=vh["cabina"]+3*unit_x, y1=(i+1)*unit_y,
                              fillcolor="yellow", line=dict(color="black"))
                fig.add_annotation(x=vh["cabina"]+2.5*unit_x, y=i*unit_y+0.5,
                                   text=f"SALDO #{s['ref']} DE {s['cantidad']} UNIDADES",
                                   showarrow=False, font=dict(size=8))

    fig.update_layout(title="Plano de cargue tipo MULA/SENCILLO",
                      xaxis=dict(title="Largo del vehículo", range=[0,vh["largo"]+1]),
                      yaxis=dict(title="Ancho del vehículo", range=[0,vh["ancho"]+1]),
                      height=400, showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Pega un pedido para generar la simulación.")
