import streamlit as st
import re
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador de Cargue 2D - Camión", page_icon="🚛", layout="wide")

# Productos
PRODUCTOS_BASE = {
    "5": {"peso": 14.77, "paquete": 130},
    "6": {"peso": 17.72, "paquete": 130},
    "8": {"peso": 23.63, "paquete": 130},
    "10": {"peso": 29.54, "paquete": 100},
}

# Vehículo
VEHICULO = {"tipo":"SENCILLO", "capacidad":10000, "largo":20, "ancho":5, "cabina":4}

# Sidebar
with st.sidebar:
    st.header("Pedido")
    raw = st.text_area("Pega el pedido aquí", height=300, placeholder="Ejemplo:\nTEJA FLEXIFORTE #5 500")

# Procesar pedido flexible
pedido_items = []
if raw:
    lines = raw.strip().split("\n")
    for line in lines:
        line_upper = line.upper().strip()
        # Buscar referencia #
        match_ref = re.search(r"#(\d+)", line_upper)
        if match_ref:
            ref = match_ref.group(1)
            # Buscar cantidad al final de la línea
            nums = re.findall(r"(\d+)\s*$", line_upper)
            if nums:
                cant = int(nums[0])
                pedido_items.append({"ref":ref, "cantidad":cant})

# Dibujar camión
if pedido_items:
    fig = go.Figure()
    # Cabina azul
    fig.add_shape(type="rect", x0=0, y0=0, x1=VEHICULO["cabina"], y1=VEHICULO["ancho"],
                  fillcolor="blue", line=dict(color="black", width=2))
    # Planchón gris
    fig.add_shape(type="rect", x0=VEHICULO["cabina"], y0=0, x1=VEHICULO["largo"], y1=VEHICULO["ancho"],
                  fillcolor="lightgray", line=dict(color="black", width=2))

    # Dibujar paquetes y saldos
    fila = 0
    unit_x = 2
    unit_y = 1
    max_col = int((VEHICULO["largo"]-VEHICULO["cabina"])/unit_x)
    max_row = int(VEHICULO["ancho"]/unit_y)

    paquetes = []
    saldos = []
    for item in pedido_items:
        paq_size = PRODUCTOS_BASE[item["ref"]]["paquete"]
        completos = item["cantidad"] // paq_size
        sobrante = item["cantidad"] % paq_size
        for _ in range(completos):
            paquetes.append(item)
        if sobrante>0:
            saldos.append({"ref":item["ref"], "cantidad":sobrante})

    for i in range(max_row):
        if i < len(paquetes):
            # Paquete central
            p = paquetes[i]
            x0 = VEHICULO["cabina"] + unit_x
            y0 = i*unit_y
            x1 = x0 + unit_x - 0.1
            y1 = y0 + unit_y - 0.1
            fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                          fillcolor="red", line=dict(color="black"))
            fig.add_annotation(x=x0+unit_x/2, y=y0+0.5, text=f"TEJA#{p['ref']}",
                               showarrow=False, font=dict(size=10))

            # Saldo izquierda
            if i < len(saldos):
                s = saldos[i]
                fig.add_shape(type="rect", x0=VEHICULO["cabina"], y0=i*unit_y,
                              x1=VEHICULO["cabina"]+unit_x, y1=(i+1)*unit_y,
                              fillcolor="yellow", line=dict(color="black"))
                fig.add_annotation(x=VEHICULO["cabina"]+unit_x/2, y=y0+0.5,
                                   text=f"SALDO #{s['ref']} DE {s['cantidad']}", showarrow=False, font=dict(size=8))
            # Saldo derecha
            if i < len(saldos):
                s = saldos[i]
                fig.add_shape(type="rect", x0=VEHICULO["cabina"]+2*unit_x, y0=i*unit_y,
                              x1=VEHICULO["cabina"]+3*unit_x, y1=(i+1)*unit_y,
                              fillcolor="yellow", line=dict(color="black"))
                fig.add_annotation(x=VEHICULO["cabina"]+2.5*unit_x, y=y0+0.5,
                                   text=f"SALDO #{s['ref']} DE {s['cantidad']}", showarrow=False, font=dict(size=8))

    fig.update_layout(title="Plano superior camión con tejas",
                      xaxis=dict(range=[0,VEHICULO["largo"]+1]), 
                      yaxis=dict(range=[0,VEHICULO["ancho"]+1]),
                      height=400, showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Pega un pedido para generar la simulación.")
