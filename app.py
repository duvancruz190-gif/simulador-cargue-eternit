import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Sistema de Cargue Eternit - Teja #4", layout="wide")

# -----------------------
# ESTILOS CSS
# -----------------------
st.markdown("""
<style>
    /* Encabezado con fondo gris más oscuro y letras del mismo tamaño */
    .custom-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 25px 50px;
        background-color: #E0E0E0; /* Gris más intenso */
        border-bottom: 8px solid #E30613; /* Línea roja inferior */
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    }
    
    .brand-eternit {
        color: #E30613; /* Rojo Eternit */
        font-size: 45px; /* Tamaño igualado */
        font-weight: 900;
        font-family: 'Arial Black', Gadget, sans-serif;
        letter-spacing: -1px;
    }
    
    .brand-elementia {
        color: #1A3A5A; /* Azul oscuro Elementia */
        font-size: 45px; /* Tamaño igualado */
        font-weight: 900;
        font-family: 'Arial Black', Gadget, sans-serif;
        letter-spacing: -1px;
    }

    /* Estilos del Camión */
    .cabina {
        background: #1A3A5A;
        color: white;
        text-align: center;
        padding: 15px;
        font-weight: bold;
        border-radius: 10px 10px 0 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .celda {
        background: #27ae60;
        color: white;
        text-align: center;
        padding: 12px;
        margin: 4px;
        border-radius: 6px;
        font-weight: bold;
        border-bottom: 3px solid #1e8449;
    }
    
    .saldo {
        background: #f1c40f;
        color: black;
        padding: 12px;
        margin: 4px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        border-bottom: 3px solid #d4ac0d;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# ENCABEZADO ESTILIZADO
# -----------------------
st.markdown("""
<div class="custom-header">
    <div class="brand-eternit">ETERNIT</div>
    <div class="brand-elementia">ELEMENTIA</div>
</div>
""", unsafe_allow_html=True)

st.title("🚛 Picking de Producto: Teja de # 4")

# -----------------------
# SIDEBAR
# -----------------------
with st.sidebar:
    st.header("Entrada de Datos")
    st.write("---")
    pedido_raw = st.text_input("Ingrese cantidad de Teja de # 4", value="0")
    
    cantidad = 0
    try:
        cantidad = int(pedido_raw)
    except:
        st.error("⚠️ Ingrese un número válido")

# -----------------------
# PARÁMETROS TÉCNICOS
# -----------------------
PAQUETE = 130
MAX_PAQUETES = 20
MAX_SALDOS = 20
MAX_SALDO_UNIDAD = 60
CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (MAX_SALDOS * MAX_SALDO_UNIDAD)

# -----------------------
# LÓGICA DE CARGA
# -----------------------
if cantidad > CAPACIDAD_TOTAL:
    st.error(f"⚠️ El pedido excede la capacidad máxima ({CAPACIDAD_TOTAL} unidades).")
    st.stop()

paquetes_ok = min(cantidad // PAQUETE, MAX_PAQUETES)
sobrante = cantidad - (paquetes_ok * PAQUETE)

saldos_lista = []
while sobrante > 0:
    if sobrante >= MAX_SALDO_UNIDAD:
        saldos_lista.append(MAX_SALDO_UNIDAD)
        sobrante -= MAX_SALDO_UNIDAD
    else:
        saldos_lista.append(sobrante)
        sobrante = 0

s_izq = [s for i, s in enumerate(saldos_lista) if i % 2 == 0]
s_der = [s for i, s in enumerate(saldos_lista) if i % 2 != 0]
p_izq = paquetes_ok // 2 + paquetes_ok % 2
p_der = paquetes_ok // 2

# -----------------------
# DISTRIBUCIÓN VISUAL
# -----------------------
col_izq, col_der = st.columns([3, 1])

with col_izq:
    st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
    
    h1, h2, h3, h4 = st.columns([1,1,1,1])
    h1.caption("Saldo Izq")
    h2.caption("Paquetes (130)")
    h3.caption("Paquetes (130)")
    h4.caption("Saldo Der")

    for i in range(10):
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        
        with c1:
            val = s_izq[i] if i < len(s_izq) else ""
            st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)
        with c2:
            val = "130" if i < p_izq else ""
            st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
        with c3:
            val = "130" if i < p_der else ""
            st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
        with c4:
            val = s_der[i] if i < len(s_der) else ""
            st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)

with col_der:
    st.subheader("📋 Resumen")
    st.info(f"**Material:** Teja de # 4")
    
    st.table({
        "Detalle": ["Total Unidades", "Paquetes", "Saldos", "Espacio Libre"],
        "Valor": [cantidad, paquetes_ok, len(saldos_lista), CAPACIDAD_TOTAL - cantidad]
    })
