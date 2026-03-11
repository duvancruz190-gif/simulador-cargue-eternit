import streamlit as st

st.set_page_config(page_title="Sistema de Cargue Eternit - Teja #4", layout="wide")

# -----------------------
# ESTILOS
# -----------------------
st.markdown("""
<style>
.header {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 50px;
    padding: 20px;
    border-bottom: 4px solid #1B5E20;
    margin-bottom: 20px;
    background-color: white;
}

.cabina {
    background: #34495e;
    color: white;
    text-align: center;
    padding: 15px;
    font-weight: bold;
    border-radius: 10px 10px 0 0;
    margin-bottom: 10px;
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

.titulo-seccion {
    font-size: 18px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 10px;
    color: #1B5E20;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# LOGOS (Eternit & Elementia)
# -----------------------
st.markdown("""
<div class="header">
    <img src="https://eternit.com.co/images/logo.png" width="200">
    <img src="https://logowik.com/content/uploads/images/elementia5222.logowik.com.webp" width="180">
</div>
""", unsafe_allow_html=True)

st.title("🚛 Sistema de Picking: Teja #4")

# -----------------------
# CONFIGURACIÓN DE PEDIDO EN SIDEBAR
# -----------------------
with st.sidebar:
    st.header("Configuración de Carga")
    st.info("Ingrese la cantidad total de **Teja #4** para calcular la distribución.")
    
    # Cambio solicitado: Etiqueta específica para Teja #4
    pedido = st.text_input("Cantidad de Teja #4", placeholder="Ej: 2800")

    cantidad = 0
    if pedido:
        try:
            cantidad = int(pedido.strip())
        except ValueError:
            st.error("⚠️ Por favor, ingrese solo números.")

# -----------------------
# PARÁMETROS TÉCNICOS
# -----------------------
PAQUETE = 130
MAX_PAQUETES = 20
MAX_SALDOS = 20
MAX_SALDO_UNIDAD = 60
CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (MAX_SALDOS * MAX_SALDO_UNIDAD)

# -----------------------
# VALIDACIÓN Y CÁLCULOS
# -----------------------
if cantidad > CAPACIDAD_TOTAL:
    st.error(f"🚫 **Capacidad Excedida**: El pedido de {cantidad} tejas no cabe en el vehículo. (Máx: {CAPACIDAD_TOTAL})")
    st.stop()

# Cálculo de paquetes completos
paquetes_reales = min(cantidad // PAQUETE, MAX_PAQUETES)
resto = cantidad - (paquetes_reales * PAQUETE)

# Cálculo de saldos (unidades sueltas o paquetes incompletos)
saldos = []
temp_resto = resto
while temp_resto > 0:
    if temp_resto >= MAX_SALDO_UNIDAD:
        saldos.append(MAX_SALDO_UNIDAD)
        temp_resto -= MAX_SALDO_UNIDAD
    else:
        saldos.append(temp_resto)
        temp_resto = 0

# Distribución de carga (Izquierda / Derecha)
saldo_izq = [s for i, s in enumerate(saldos) if i % 2 == 0]
saldo_der = [s for i, s in enumerate(saldos) if i % 2 != 0]

izq_paquetes = paquetes_reales // 2 + paquetes_reales % 2
der_paquetes = paquetes_reales // 2

# -----------------------
# VISUALIZACIÓN
# -----------------------
col_grafico, col_resumen = st.columns([3, 1])

with col_grafico:
    st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
    
    # Encabezados de columnas
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    c1.markdown('<p class="titulo-seccion">Saldos Izq.</p>', unsafe_allow_html=True)
    c2.markdown('<p class="titulo-seccion">Paquetes Izq.</p>', unsafe_allow_html=True)
    c3.markdown('<p class="titulo-seccion">Paquetes Der.</p>', unsafe_allow_html=True)
    c4.markdown('<p class="titulo-seccion">Saldos Der.</p>', unsafe_allow_html=True)

    # Renderizado de la cama del camión (10 filas)
    for i in range(10):
        r1, r2, r3, r4 = st.columns([1, 1, 1, 1])
        
        with r1: # Saldos Izquierda
            val = saldo_izq[i] if i < len(saldo_izq) else ""
            st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)
            
        with r2: # Paquetes Izquierda
            val = PAQUETE if i < izq_paquetes else ""
            st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
            
        with r3: # Paquetes Derecha
            val = PAQUETE if i < der_paquetes else ""
            st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
            
        with r4: # Saldos Derecha
            val = saldo_der[i] if i < len(saldo_der) else ""
            st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)

with col_resumen:
    st.subheader("📊 Resumen de Carga")
    st.write(f"**Material:** Teja #4")
    
    resumen_data = {
        "Concepto": [
            "Total Unidades",
            "Paquetes de 130",
            "Cantidad de Saldos",
            "Espacio Disponible"
        ],
        "Valor": [
            f"{cantidad} und",
            f"{paquetes_reales}",
            f"{len(saldos)}",
            f"{CAPACIDAD_TOTAL - cantidad} und"
        ]
    }
    st.table(resumen_data)
    
    if cantidad > 0:
        st.success("✅ Distribución calculada correctamente.")
