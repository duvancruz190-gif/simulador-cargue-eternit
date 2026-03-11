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
    min-height: 45px;
}
.saldo{
    background:#f1c40f;
    color:black;
    padding:12px;
    margin:4px;
    border-radius:6px;
    text-align:center;
    font-weight:bold;
    min-height: 45px;
}
.titulo{
    font-size:20px;
    font-weight:bold;
    text-align:center;
    margin-bottom:10px;
}
/* Estilo para ocultar el botón al imprimir */
@media print {
    .no-print {
        display: none !important;
    }
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
# PEDIDO (Sidebar)
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
    st.error(f"🚫 El pedido no cabe en la mula. Capacidad máxima: {CAPACIDAD_TOTAL} tejas")
    st.stop()

# -----------------------
# CÁLCULOS
# -----------------------
paquetes = min(cantidad // PAQUETE, MAX_PAQUETES)
resto = cantidad - (paquetes * PAQUETE)

saldos = []
while resto > 0:
    if resto >= MAX_SALDO_UNIDAD:
        saldos.append(MAX_SALDO_UNIDAD)
        resto -= MAX_SALDO_UNIDAD
    else:
        saldos.append(resto)
        resto = 0

saldo_izq = [s for i, s in enumerate(saldos) if i % 2 == 0]
saldo_der = [s for i, s in enumerate(saldos) if i % 2 != 0]

izq = paquetes // 2 + paquetes % 2
der = paquetes // 2

# -----------------------
# LAYOUT PRINCIPAL
# -----------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<div class="cabina">CABINA</div>', unsafe_allow_html=True)
    st.markdown("<div class='titulo'>Saldos Izquierda | Paquetes | Saldos Derecha</div>", unsafe_allow_html=True)

    filas = 10
    for i in range(filas):
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        with c1:
            val = saldo_izq[i] if i < len(saldo_izq) else ""
            st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)
        with c2:
            val = "130" if i < izq else ""
            st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
        with c3:
            val = "130" if i < der else ""
            st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
        with c4:
            val = saldo_der[i] if i < len(saldo_der) else ""
            st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)

with col2:
    st.subheader("Resumen")
    st.table({
        "Concepto": ["Cantidad pedida", "Paquetes planchón", "Saldos", "Capacidad máx."],
        "Valor": [cantidad, paquetes, len(saldos), CAPACIDAD_TOTAL]
    })

# -----------------------
# BOTÓN DE IMPRESIÓN CORREGIDO
# -----------------------
st.markdown("""
    <div class="no-print" style="text-align:center; padding:20px;">
        <button onclick="window.parent.window.print();" style="
            background-color: #1B5E20;
            color: white;
            padding: 15px 32px;
            text-align: center;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
            border: none;
            font-weight: bold;
        ">
            🖨️ IMPRIMIR PLAN DE CARGUE
        </button>
    </div>
""", unsafe_allow_html=True)
