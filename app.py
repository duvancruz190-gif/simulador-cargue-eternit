import streamlit as st

st.set_page_config(page_title="Sistema de Cargue Eternit - Teja #4", layout="wide")

# -----------------------
# ESTILOS CORREGIDOS
# -----------------------
st.markdown("""
<style>
.header {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 80px;
    padding: 20px;
    border-bottom: 5px solid #1B5E20;
    margin-bottom: 30px;
    background-color: white;
}
.header img {
    max-height: 80px;
    width: auto;
}
.cabina {
    background: #34495e;
    color: white;
    text-align: center;
    padding: 15px;
    font-weight: bold;
    border-radius: 10px 10px 0 0;
    margin-bottom: 10px;
}
.celda {
    background: #27ae60;
    color: white;
    text-align: center;
    padding: 12px;
    margin: 4px;
    border-radius: 6px;
    font-weight: bold;
}
.saldo {
    background: #f1c40f;
    color: black;
    padding: 12px;
    margin: 4px;
    border-radius: 6px;
    text-align: center;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# LOGOS (URLs actualizadas para evitar errores)
# -----------------------
# He usado una técnica para centrar mejor y asegurar que carguen
st.markdown("""
<div class="header">
    <img src="https://eternit.com.co/images/logo.png">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Elementia_logo.png/640px-Elementia_logo.png">
</div>
""", unsafe_allow_html=True)

st.title("🚛 Picking de Producto: Teja de # 4")

# -----------------------
# PEDIDO (SIDEBAR)
# -----------------------
with st.sidebar:
    st.header("Entrada de Datos")
    # Cambio solicitado: Etiqueta específica
    pedido = st.text_input("Ingrese cantidad de Teja de # 4")
    
    cantidad = 0
    if pedido:
        try:
            cantidad = int(pedido.strip())
        except ValueError:
            st.error("Por favor, ingrese solo números")

# -----------------------
# PARÁMETROS Y LÓGICA
# -----------------------
PAQUETE = 130
MAX_PAQUETES = 20
MAX_SALDOS = 20
MAX_SALDO_UNIDAD = 60
CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (MAX_SALDOS * MAX_SALDO_UNIDAD)

if cantidad > CAPACIDAD_TOTAL:
    st.error(f"⚠️ El pedido excede la capacidad de la mula ({CAPACIDAD_TOTAL} unidades).")
    st.stop()

# Cálculos
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

# Distribución
saldo_izq = [s for i, s in enumerate(saldos) if i % 2 == 0]
saldo_der = [s for i, s in enumerate(saldos) if i % 2 != 0]
izq = paquetes // 2 + paquetes % 2
der = paquetes // 2

# -----------------------
# LAYOUT VISUAL
# -----------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<div class="cabina">CABINA / FRENTE</div>', unsafe_allow_html=True)
    
    # Encabezados
    h1, h2, h3, h4 = st.columns([1,1,1,1])
    h1.caption("Saldo Izq")
    h2.caption("Paquetes")
    h3.caption("Paquetes")
    h4.caption("Saldo Der")

    for i in range(10):
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
    st.subheader("Resumen Teja #4")
    st.table({
        "Concepto": ["Total Unidades", "Paquetes", "Saldos", "Espacio Libre"],
        "Valor": [cantidad, paquetes, len(saldos), CAPACIDAD_TOTAL - cantidad]
    })
