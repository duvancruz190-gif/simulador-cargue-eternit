import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Sistema de Cargue Eternit - Teja #4", layout="wide")

# -----------------------
# ESTILOS CSS (DISEÑO CORPORATIVO)
# -----------------------
st.markdown("""
<style>
    /* Encabezado alternativo sin imágenes externas para evitar errores */
    .custom-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        background-color: #f8f9fa;
        border-bottom: 5px solid #1B5E20;
        border-radius: 10px;
        margin-bottom: 25px;
    }
    .brand-eternit {
        color: #1B5E20;
        font-size: 32px;
        font-weight: bold;
        font-family: Arial, sans-serif;
    }
    .brand-elementia {
        color: #555;
        font-size: 24px;
        font-weight: lighter;
        font-family: sans-serif;
    }
    
    /* Estilos del Camión */
    .cabina {
        background: #34495e;
        color: white;
        text-align: center;
        padding: 15px;
        font-weight: bold;
        border-radius: 10px 10px 0 0;
    }
    .celda {
        background: #27ae60;
        color: white;
        text-align: center;
        padding: 12px;
        margin: 4px;
        border-radius: 6px;
        font-weight: bold;
        border: 1px solid #1e8449;
    }
    .saldo {
        background: #f1c40f;
        color: black;
        padding: 12px;
        margin: 4px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #d4ac0d;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# ENCABEZADO (TEXTO ESTILIZADO PARA QUE NUNCA FALLE)
# -----------------------
st.markdown("""
<div class="custom-header">
    <div class="brand-eternit">ETERNIT ®</div>
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
    # Campo específico solicitado
    pedido_raw = st.text_input("Ingrese cantidad de Teja de # 4", value="0")
    
    cantidad = 0
    try:
        cantidad = int(pedido_raw)
    except:
        st.error("⚠️ Ingrese un número válido.")

# -----------------------
# LÓGICA TÉCNICA
# -----------------------
PAQUETE = 130
MAX_PAQUETES = 20
MAX_SALDOS = 20
MAX_SALDO_UNIDAD = 60
CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (MAX_SALDOS * MAX_SALDO_UNIDAD)

if cantidad > CAPACIDAD_TOTAL:
    st.error(f"⚠️ El pedido excede la capacidad máxima ({CAPACIDAD_TOTAL} tejas).")
    st.stop()

# Cálculos de distribución
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
# REPRESENTACIÓN VISUAL
# -----------------------
col_camion, col_resumen = st.columns([3, 1])

with col_camion:
    st.markdown('<div class="cabina">FRENTE / CABINA DEL VEHÍCULO</div>', unsafe_allow_html=True)
    
    # Cabeceras del diagrama
    h1, h2, h3, h4 = st.columns([1,1,1,1])
    h1.caption("Saldo Izq")
    h2.caption("Paquetes (130)")
    h3.caption("Paquetes (130)")
    h4.caption("Saldo Der")

    # Renderizado de filas
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

with col_resumen:
    st.subheader("📋 Resumen")
    st.info(f"**Producto:** Teja de # 4")
    
    st.table({
        "Concepto": ["Cant. Total", "Paquetes", "Saldos", "Disponible"],
        "Valor": [cantidad, paquetes_ok, len(saldos_lista), CAPACIDAD_TOTAL - cantidad]
    })
