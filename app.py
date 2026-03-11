import streamlit as st

st.set_page_config(page_title="Sistema de Cargue Eternit", layout="wide")

# -----------------------
# ESTILOS
# -----------------------

st.markdown("""
<style>

.header{
display:flex;
justify-content:center;
gap:60px;
padding:10px;
border-bottom:4px solid #1B5E20;
margin-bottom:20px;
}

.cabina{
background:#7f8c8d;
color:white;
text-align:center;
padding:12px;
font-weight:bold;
border-radius:10px;
margin-bottom:20px;
}

.celda{
background:#27ae60;
color:white;
text-align:center;
padding:12px;
margin:4px;
border-radius:6px;
font-weight:bold;
}

.saldo{
background:#f1c40f;
color:black;
padding:12px;
margin:4px;
border-radius:6px;
text-align:center;
font-weight:bold;
}

.titulo{
font-size:20px;
font-weight:bold;
text-align:center;
margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------
# LOGOS
# -----------------------

st.markdown("""
<div class="header">
<img src="https://eternit.com.ec/wp-content/uploads/2024/08/logo-eternit-400x150-1.png" width="200">
<img src="https://logowik.com/content/uploads/images/elementia5222.logowik.com.webp" width="200">
</div>
""", unsafe_allow_html=True)

st.title("🚛 Sistema de Picking - Eternit Colombia")

# -----------------------
# PEDIDO
# -----------------------

with st.sidebar:

    st.header("Pedido")

    pedido = st.text_area("Pegue la cantidad")

    cantidad = 0

    if pedido:
        try:
            cantidad = int(pedido.strip())
        except:
            st.warning("Solo números")

# -----------------------
# PARÁMETROS
# -----------------------

PAQUETE = 130
MAX_PAQUETES = 20

MAX_SALDOS = 20
MAX_SALDO_UNIDAD = 60

CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (MAX_SALDOS * MAX_SALDO_UNIDAD)

# -----------------------
# VALIDACIÓN
# -----------------------

if cantidad > CAPACIDAD_TOTAL:

    st.error(f"""
🚫 El pedido no cabe en la mula

Capacidad máxima: {CAPACIDAD_TOTAL} tejas
""")

    st.stop()

# -----------------------
# CÁLCULO PAQUETES
# -----------------------

paquetes = min(cantidad // PAQUETE, MAX_PAQUETES)

resto = cantidad - (paquetes * PAQUETE)

# -----------------------
# SALDOS
# -----------------------

saldos = []

while resto > 0:

    if resto >= MAX_SALDO_UNIDAD:
        saldos.append(MAX_SALDO_UNIDAD)
        resto -= MAX_SALDO_UNIDAD
    else:
        saldos.append(resto)
        resto = 0

# distribución equilibrada

saldo_izq = []
saldo_der = []

for i,s in enumerate(saldos):

    if i % 2 == 0:
        saldo_izq.append(s)
    else:
        saldo_der.append(s)

# paquetes izquierda derecha

izq = paquetes // 2 + paquetes % 2
der = paquetes // 2

# -----------------------
# LAYOUT
# -----------------------

col1, col2 = st.columns([3,1])

# -----------------------
# DIAGRAMA CAMIÓN
# -----------------------

with col1:

    st.markdown('<div class="cabina">CABINA</div>', unsafe_allow_html=True)

    st.markdown(
        "<div class='titulo'>Saldos Izquierda &nbsp;&nbsp;&nbsp;&nbsp; Paquetes &nbsp;&nbsp;&nbsp;&nbsp; Saldos Derecha</div>",
        unsafe_allow_html=True
    )

    filas = 10

    for i in range(filas):

        c1, c2, c3, c4 = st.columns([1,1,1,1])

        with c1:

            if i < len(saldo_izq):
                st.markdown(f'<div class="saldo">{saldo_izq[i]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="saldo"></div>', unsafe_allow_html=True)

        with c2:

            if i < izq:
                st.markdown('<div class="celda">130</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="celda"></div>', unsafe_allow_html=True)

        with c3:

            if i < der:
                st.markdown('<div class="celda">130</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="celda"></div>', unsafe_allow_html=True)

        with c4:

            if i < len(saldo_der):
                st.markdown(f'<div class="saldo">{saldo_der[i]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="saldo"></div>', unsafe_allow_html=True)

# -----------------------
# TABLA
# -----------------------

with col2:

    st.subheader("Resumen")

    st.table({

        "Concepto":[
            "Cantidad pedida",
            "Paquetes planchón",
            "Saldos",
            "Capacidad máxima"
        ],

        "Valor":[
            cantidad,
            paquetes,
            len(saldos),
            CAPACIDAD_TOTAL
        ]

    })
st.markdown("""
<script>
function imprimir() {
    window.print();
}
</script>

<button onclick="imprimir()" style="
background:#1B5E20;
color:white;
padding:10px 20px;
border:none;
border-radius:6px;
font-size:16px;
cursor:pointer;">
🖨️ Imprimir
</button>
""", unsafe_allow_html=True)
