import streamlit as st
import math

# ---------------------------
# LOGIN
# ---------------------------

USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.image("ETERNIT LOGOS.webp", width=200)

    st.markdown(
        "<h3 style='text-align:center;color:red;'>Simulador de Cargue</h3>",
        unsafe_allow_html=True
    )

    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        if usuario.upper() == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()


# ---------------------------
# PRODUCTOS (TEJAS)
# ---------------------------

PRODUCTOS = {
    "TEJA FLEXIFORTE #4": {"largo":4,"peso":11.82,"paquete":130},
    "TEJA FLEXIFORTE #5": {"largo":5,"peso":14.77,"paquete":130},
    "TEJA FLEXIFORTE #6": {"largo":6,"peso":17.72,"paquete":130},
    "TEJA FLEXIFORTE #8": {"largo":8,"peso":23.63,"paquete":130},
    "TEJA FLEXIFORTE #10": {"largo":10,"peso":29.54,"paquete":100},
}

# ---------------------------
# VEHICULOS
# ---------------------------

VEHICULOS = [

    {"tipo":"TURBO","largo":16,"capacidad":5000},
    {"tipo":"SENCILLO","largo":20,"capacidad":10000},
    {"tipo":"DOBLE TROQUE","largo":24,"capacidad":18000},
    {"tipo":"CUATRO MANOS","largo":28,"capacidad":22000},
    {"tipo":"MULA","largo":40,"capacidad":34000}

]


# ---------------------------
# INTERFAZ
# ---------------------------

st.image("ETERNIT LOGOS.webp", width=200)

st.markdown(
    "<h3 style='text-align:center;color:red;'>Simulador de Cargue</h3>",
    unsafe_allow_html=True
)

st.write("")

ref = st.selectbox("Referencia de Teja", list(PRODUCTOS.keys()))

cantidad = st.number_input("Cantidad de unidades", min_value=0)

if st.button("Calcular Cargue"):

    datos = PRODUCTOS[ref]

    largo_teja = datos["largo"]
    peso_teja = datos["peso"]
    paquete = datos["paquete"]

    # ---------------------------
    # CALCULOS BASICOS
    # ---------------------------

    peso_total = cantidad * peso_teja

    paquetes_totales = math.ceil(cantidad / paquete)

    vehiculo_elegido = None

    for vh in VEHICULOS:

        if peso_total <= vh["capacidad"]:
            vehiculo_elegido = vh
            break

    if vehiculo_elegido is None:
        st.error("No hay vehículo disponible para ese peso")
        st.stop()

    largo_planchon = vehiculo_elegido["largo"]

    # ---------------------------
    # LOGICA DEL PLANCHON
    # ---------------------------

    paquetes_lado = largo_planchon // largo_teja

    paquetes_planchon = paquetes_lado * 2

    pasos_usados = paquetes_lado * largo_teja

    sobrante = largo_planchon - pasos_usados

    # paquete atravesado

    if sobrante >= 4:
        atravesado = 1
    else:
        atravesado = 0

    capacidad_planchon = paquetes_planchon + atravesado

    # saldo arriba

    saldo = paquetes_totales - capacidad_planchon

    if saldo > 0:
        arriba = min(saldo,60)
    else:
        arriba = 0

    # ---------------------------
    # RESULTADOS
    # ---------------------------

    st.subheader("Resultado del Cargue")

    c1,c2,c3 = st.columns(3)

    c1.metric("Vehículo", vehiculo_elegido["tipo"])
    c2.metric("Peso total (kg)", round(peso_total,2))
    c3.metric("Paquetes", paquetes_totales)

    st.write("")

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric("Paquetes por lado", paquetes_lado)
    c2.metric("Planchón", paquetes_planchon)
    c3.metric("Atravesado", atravesado)
    c4.metric("Arriba", arriba)
    c5.metric("Pasos sobrantes", sobrante)
