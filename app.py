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

/* OCULTAR ELEMENTOS AL IMPRIMIR */
@media print {
    .no-print, .stSidebar, header, footer {
        display: none !important;
    }
    .main {
        padding: 0px !important;
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
# PEDIDO (Barra Lateral)
# -----------------------
with st.sidebar:
    st.header("Configuración")
    pedido = st.text_input("Ingrese la cantidad total", value="0")
    cantidad = 0
    try:
        cantidad = int(pedido)
    except:
        st.warning("Ingrese solo números")

# -----------------------
# PARÁMETROS DE CARGA
# -----------------------
PAQUETE = 130
MAX_PAQUETES = 20
MAX_SALDO_UNIDAD = 60
CAPACIDAD_TOTAL = 3800 # Ajustado a capacidad real aproximada

# -----------------------
# CÁLCULOS
# -----------------------
if cantidad > 0:
    if cantidad > CAPACIDAD_TOTAL:
        st.error(f"🚫 Excede capacidad máxima ({CAPACIDAD_TOTAL})")
        st.stop()

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
    # VISUALIZACIÓN
    # -----------------------
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="cabina">CABINA</div>', unsafe_allow_html=True)
        st.markdown("<div class='titulo'>Saldos Izq | Paquetes | Saldos Der</div>", unsafe_allow_html=True)

        for i in range(10):
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            with c1:
                v = saldo_izq[i] if i < len(saldo_izq) else ""
                st.markdown(f'<div class="saldo">{v}</div>', unsafe_allow_html=True)
            with c2:
                v = "130" if i < izq else ""
                st.markdown(f'<div class="celda">{v}</div>', unsafe_allow_html=True)
            with c3:
                v = "130" if i < der else ""
                st.markdown(f'<div class="celda">{v}</div>', unsafe_allow_html=True)
            with c4:
                v = saldo_der[i] if i < len(saldo_der) else ""
                st.markdown(f'<div class="saldo">{v}</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("Resumen")
        st.write(f"**Total:** {cantidad} tejas")
        st.write(f"**Paquetes:** {paquetes}")
        st.write(f"**Saldos:** {len(saldos)}")

# -----------------------
# BOTÓN DE IMPRESIÓN (EL QUE SÍ FUNCIONA)
# -----------------------
st.markdown("""
    <div class="no-print" style="margin-top: 30px; text-align: center;">
        <button onclick="window.print();" style="
            background-color: #1B5E20;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
        ">
            🖨️ IMPRIMIR PLAN DE DESPACHO
        </button>
    </div>
    <script>
        // Este script ayuda a que el botón funcione incluso dentro del iframe
        const button = window.parent.document.querySelector('button');
        button.addEventListener('click', () => {
            window.parent.print();
        });
    </script>
""", unsafe_allow_html=True)
