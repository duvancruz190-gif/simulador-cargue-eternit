import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Sistema de Cargue Eternit - Teja #4", layout="wide")

# -----------------------
# ESTILOS CSS (DISEÑO CORPORATIVO ROJO)
# -----------------------
st.markdown("""
<style>
    /* Encabezado con Colores de Marca */
    .custom-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 25px 40px;
        background-color: white;
        border-bottom: 6px solid #E30613; /* Rojo Eternit */
        border-radius: 8px;
        margin-bottom: 30px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    
    .brand-eternit {
        color: #E30613; /* Rojo Original */
        font-size: 42px;
        font-weight: 900;
        font-family: 'Arial Black', Gadget, sans-serif;
        letter-spacing: -2px;
    }
    
    .brand-elementia {
        color: #2c3e50; /* Azul Grisáceo Elementia */
        font-size: 28px;
        font-weight: bold;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 1px;
    }

    /* Estilos del Camión */
    .cabina {
        background: #2c3e50;
        color: white;
        text-align: center;
        padding: 15px;
        font-weight: bold;
        border-radius: 10px 10px 0 0;
        text-transform: uppercase;
    }
    .celda {
        background: #27ae60; /* Verde para los paquetes llenos */
        color: white;
        text-align: center;
        padding: 12px;
        margin: 4px;
        border-radius: 6px;
        font-weight: bold;
        border-bottom: 3px solid #1e8449;
    }
    .saldo {
        background: #f1c40f; /* Amarillo para los saldos */
        color: black;
        padding: 12px;
        margin: 4px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        border-bottom: 3px solid #d4ac0d;
    }
    
    /* Ajustes de Títulos */
    h1 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# ENCABEZADO (CON EL LOGO ROJO SIMULADO)
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
    st.header("Configuración")
    st.write("---")
    # Campo específico: Teja de # 4
    pedido_raw = st.text_input("Ingrese cantidad de Teja de # 4", value="0")
    
    cantidad = 0
    try:
        cantidad = int(pedido_raw)
    except:
        st.error("⚠️ Ingrese un número válido")

# -----------------------
# LÓGICA DE CARGA
# -----------------------
PAQUETE = 130
MAX_PAQUETES = 20
MAX_SALDOS = 20
MAX_SALDO_UNIDAD = 60
CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (MAX_SALDOS * MAX_SALDO_UNIDAD)

if cantidad > CAPACIDAD_TOTAL:
    st.error(f"⚠️ El pedido de {cantidad} unidades excede la capacidad máxima de la mula ({CAPACIDAD_TOTAL}).")
    st.stop()

# Cálculos
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
# DIAGRAMA Y TABLA
# -----------------------
col_izq, col_der = st.columns([3, 1])

with col_izq:
    st.markdown('<div class="cabina">VISTA SUPERIOR: FRENTE DEL CAMIÓN</div>', unsafe_allow_html=True)
    
    # Cabeceras de columna
    h1, h2, h3, h4 = st.columns([1,1,1,1])
    h1.caption("Saldos Izq")
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
    st.subheader("📊 Reporte")
    st.info(f"**Material:** Teja de # 4")
    
    st.table({
        "Detalle": ["Total Unidades", "Paquetes Completos", "Saldos Generados", "Capacidad Libre"],
        "Valor": [cantidad, paquetes_ok, len(saldos_lista), CAPACIDAD_TOTAL - cantidad]
    })
    
    if cantidad > 0:
        st.success("Distribución lista para cargue.")
