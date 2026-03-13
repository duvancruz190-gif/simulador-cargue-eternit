import streamlit as st
import math

# -----------------------------
# LOGIN
# -----------------------------

USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

# -----------------------------
# PRODUCTOS (TEJAS FLEXIFORTE)
# peso por unidad en kg
# largo_ft = numero de la teja
# -----------------------------

PRODUCTOS = {
    "TEJA FLEXIFORTE #4": {"largo_ft":4,"peso":11.82,"paquete":130},
    "TEJA FLEXIFORTE #5": {"largo_ft":5,"peso":14.77,"paquete":130},
    "TEJA FLEXIFORTE #6": {"largo_ft":6,"peso":17.72,"paquete":130},
    "TEJA FLEXIFORTE #8": {"largo_ft":8,"peso":23.63,"paquete":130},
    "TEJA FLEXIFORTE #10": {"largo_ft":10,"peso":29.54,"paquete":100},
}

# -----------------------------
# VEHICULOS
# capacidad en kg
# largo en pasos
# -----------------------------

VEHICULOS = [

    {
        "tipo":"TURBO",
        "largo_planchon":16,
        "capacidad":5000
    },

    {
        "tipo":"SENCILLO",
        "largo_planchon":20,
        "capacidad":10000
    },

    {
        "tipo":"DOBLE TROQUE",
        "largo_planchon":24,
        "capacidad":18000
    },

    {
        "tipo":"CUATRO MANOS",
        "largo_planchon":28,
        "capacidad":22000
    },

    {
        "tipo":"MULA",
        "largo_planchon":40,
        "capacidad":34000
    }

]

# -----------------------------
# FUNCION LOGICA DE CARGUE
# -----------------------------

def calcular_cargue(ref, cantidad):

    datos = PRODUCTOS[ref]

    largo_teja = datos["largo_ft"]
    peso_unit = datos["peso"]
    paquete = datos["paquete"]

    peso_total = cantidad * peso_unit

    paquetes_totales = math.ceil(cantidad / paquete)

    for vh in VEHICULOS:

        largo = vh["largo_planchon"]

        # paquetes por lado
        paquetes_lado = largo // largo_teja

        # planchon
        paquetes_planchon = paquetes_lado * 2

        pasos_usados = paquetes_lado * largo_teja

        sobrante = largo - pasos_usados

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

        if peso_total <= vh["capacidad"]:
            return {
                "vehiculo":vh["tipo"],
                "peso_total":peso_total,
                "paquetes_totales":paquetes_totales,
                "paquetes_lado":paquetes_lado,
                "planchon":paquetes_planchon,
                "atravesado":atravesado,
                "arriba":arriba,
                "sobrante":sobrante
            }

    return None


# -----------------------------
# CONTROL LOGIN
# -----------------------------

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

# -----------------------------
# SISTEMA
# -----------------------------

st.image("ETERNIT LOGOS.webp", width=200)

st.markdown(
    "<h3 style='text-align:center;color:red;'>Simulador de Cargue</h3>",
    unsafe_allow_html=True
)

st.write("")

ref = st.selectbox(
    "Referencia",
    list(PRODUCTOS.keys())
)

cantidad = st.number_input(
    "Cantidad de unidades",
    min_value=0
)

if st.button("Calcular Cargue"):

    resultado = calcular_cargue(ref, cantidad)

    if resultado:

        st.subheader("Resultado del Cargue")

        c1,c2,c3 = st.columns(3)

        c1.metric("Vehículo", resultado["vehiculo"])
        c2.metric("Peso total kg", round(resultado["peso_total"],2))
        c3.metric("Paquetes", resultado["paquetes_totales"])

        st.write("")

        c1,c2,c3,c4,c5 = st.columns(5)

        c1.metric("Paquetes por lado", resultado["paquetes_lado"])
        c2.metric("Planchón", resultado["planchon"])
        c3.metric("Atravesado", resultado["atravesado"])
        c4.metric("Arriba", resultado["arriba"])
        c5.metric("Pasos sobrantes", resultado["sobrante"])

    else:

        st.error("No hay vehículo disponible para este pedido")
