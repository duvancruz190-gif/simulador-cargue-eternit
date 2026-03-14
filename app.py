import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go

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
# BASE DE PRODUCTOS
# -----------------------------

PRODUCTOS_BASE = {
    "4": {"peso": 11.82, "paquete": 130},
    "5": {"peso": 14.77, "paquete": 130},
    "6": {"peso": 17.72, "paquete": 130},
    "8": {"peso": 23.63, "paquete": 130},
    "10": {"peso": 29.54, "paquete": 100},
}

# -----------------------------
# VEHÍCULOS
# -----------------------------

VEHICULOS = [
    {"tipo":"TURBO","capacidad":5000},
    {"tipo":"SENCILLO","capacidad":10000},
    {"tipo":"DOBLE TROQUE","capacidad":18000},
    {"tipo":"CUATRO MANOS","capacidad":22000},
    {"tipo":"MULA","capacidad":34000},
]

# -----------------------------
# FUNCIÓN CAMIÓN 3D
# -----------------------------

def dibujar_camion(paquetes):

    fig = go.Figure()

    # CABINA
    fig.add_trace(go.Mesh3d(
        x=[-2,-1,-1,-2,-2,-1,-1,-2],
        y=[0,0,2,2,0,0,2,2],
        z=[0,0,0,0,2,2,2,2],
        color="blue",
        opacity=0.9
    ))

    # PLANCHÓN
    fig.add_trace(go.Mesh3d(
        x=[0,12,12,0,0,12,12,0],
        y=[0,0,4,4,0,0,4,4],
        z=[0,0,0,0,0.3,0.3,0.3,0.3],
        color="gray",
        opacity=0.4
    ))

    # RUEDAS
    for i in [1,4,8,11]:

        fig.add_trace(go.Scatter3d(
            x=[i],
            y=[-0.3],
            z=[0],
            mode='markers',
            marker=dict(size=10,color="black")
        ))

        fig.add_trace(go.Scatter3d(
            x=[i],
            y=[4.3],
            z=[0],
            mode='markers',
            marker=dict(size=10,color="black")
        ))

    # CARGA
    x=0.5
    y=0.3
    z=0.3

    for i in range(len(paquetes)):

        fig.add_trace(go.Mesh3d(
            x=[x,x+0.9,x+0.9,x,x,x+0.9,x+0.9,x],
            y=[y,y,y+0.9,y+0.9,y,y,y+0.9,y+0.9],
            z=[z,z,z,z,z+0.6,z+0.6,z+0.6,z+0.6],
            color="red",
            opacity=0.9
        ))

        y += 1

        if y > 3:
            y = 0.3
            x += 1

    fig.update_layout(
        title="Simulación 3D del Cargue del Camión",
        scene=dict(
            xaxis_title="Largo",
            yaxis_title="Ancho",
            zaxis_title="Altura"
        ),
        height=600
    )

    return fig


# -----------------------------
# LOGIN
# -----------------------------

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    col1,col2,col3 = st.columns([1,1.5,1])

    with col2:

        st.image("logo-eternit-400x150-1.png", use_container_width=True)

        st.markdown(
        """
        <h1 style='text-align:center;color:#1A3A5A;font-size:40px'>
        Simulador de Cargue
        </h1>
        """,
        unsafe_allow_html=True
        )

        usuario = st.text_input("Correo")
        clave = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):

            if usuario.upper() == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

# -----------------------------
# APP PRINCIPAL
# -----------------------------

else:

    st.title("🚛 Simulador Logístico de Cargue")

    with st.sidebar:

        st.header("Ingreso del Pedido")

        raw = st.text_area(
            "Pegue el pedido",
            placeholder="TEJA FLEXIFORTE #5 900"
        )

    pedido=[]
    peso_total=0

    if raw:

        lines=raw.split("\n")

        for line in lines:

            line=line.upper()

            ref=re.search(r"#(\d+)",line)

            if ref:

                r=ref.group(1)

                if r in PRODUCTOS_BASE:

                    numeros=re.findall(r"\d+",line.replace(f"#{r}",""))

                    if numeros:

                        cant=int(numeros[-1])

                        peso=cant*PRODUCTOS_BASE[r]["peso"]

                        pedido.append({
                            "Referencia":r,
                            "Cantidad":cant,
                            "Peso":peso
                        })

                        peso_total+=peso

    if pedido:

        df=pd.DataFrame(pedido)

        vh=next((v for v in VEHICULOS if v["capacidad"]>=peso_total),VEHICULOS[-1])

        toneladas=peso_total/1000

        ocupacion=(peso_total/vh["capacidad"])*100

        c1,c2,c3,c4=st.columns(4)

        c1.metric("Peso total kg",f"{peso_total:,.0f}")
        c2.metric("Toneladas",f"{toneladas:.2f}")
        c3.metric("Vehículo recomendado",vh["tipo"])
        c4.metric("Ocupación",f"{ocupacion:.1f}%")

        st.progress(min(ocupacion/100,1.0))

        st.subheader("Detalle del pedido")

        st.dataframe(df,use_container_width=True)

        paquetes=[]

        for p in pedido:

            size=PRODUCTOS_BASE[p["Referencia"]]["paquete"]

            completos=p["Cantidad"]//size

            for i in range(completos):
                paquetes.append(p)

        st.divider()

        st.subheader("Simulación 3D del cargue")

        fig=dibujar_camion(paquetes)

        st.plotly_chart(fig,use_container_width=True)

    else:

        st.info("Ingrese un pedido para generar la simulación.")
