import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Sistema de Cargue Eternit - Teja #4", layout="wide")

# -----------------------
# ESTILOS CSS
# -----------------------
st.markdown("""
<style>
    .cabina {
        background: #34495e;
        color: white;
        text-align: center;
        padding: 15px;
        font-weight: bold;
        border-radius: 10px 10px 0 0;
        margin-top: 20px;
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
    .stTable {
        background-color: #f8f9fa;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# ENCABEZADO: LOGOS Y TÍTULO
# -----------------------
# Usamos columnas de Streamlit para asegurar que las imágenes se intenten cargar correctamente
head1, head2, head3 = st.columns([2, 2, 2])

with head1:
    # Logo Eternit
    st.image("https://eternit.com.co/images/logo.png", width=200)

with head3:
    # Logo Elementia
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Elementia_logo.png/640px-Elementia_logo.png", width=180)

st.markdown("<hr style='border:2px solid #1B5E20'>", unsafe_allow_html=True)
st.title("🚛 Picking de Producto: Teja de # 4")

# -----------------------
# SIDEBAR: ENTRADA DE DATOS
# -----------------------
with st.sidebar:
    st.header("Entrada de Datos")
    st.info("Complete la información para calcular el cargue de la mula.")
    
    # Campo solicitado: Teja de # 4
    pedido_input = st.text_input("Ingrese cantidad de Teja de # 4", value="0")
    
    cantidad = 0
    try:
        cantidad = int(pedido_input)
    except ValueError:
        st.error("⚠️ Por favor, ingrese solo números enteros.")

# -----------------------
# PARÁMETROS TÉCNICOS
# -----------------------
PAQUETE = 130
MAX_PAQUETES = 20
MAX_SALDOS = 20
MAX_SALDO_UNIDAD = 60
CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (MAX_SALDOS * MAX_SALDO_UNIDAD)

# -----------------------
# LÓGICA DE CÁLCULO
# -----------------------
if cantidad > CAPACIDAD_TOTAL:
    st.error(f"🚫 El pedido ({cantidad}) supera la capacidad máxima permitida de {CAPACIDAD_TOTAL} unidades.")
    st.stop()

if cantidad > 0:
    # Calcular paquetes completos
    paquetes_total = min(cantidad // PAQUETE, MAX_PAQUETES)
    sobrante = cantidad - (paquetes_total * PAQUETE)

    # Calcular distribución de saldos
    lista_saldos = []
    temp_sobrante = sobrante
    while temp_sobrante > 0:
        if temp_sobrante >= MAX_SALDO_UNIDAD:
            lista_saldos.append(MAX_SALDO_UNIDAD)
            temp_sobrante -= MAX_SALDO_UNIDAD
        else:
            lista_saldos.append(temp_sobrante)
            temp_sobrante = 0

    # Separar en Izquierda y Derecha para el diagrama
    s_izq = [s for i, s in enumerate(lista_saldos) if i % 2 == 0]
    s_der = [s for i, s in enumerate(lista_saldos) if i % 2 != 0]
    
    p_izq = paquetes_total // 2 + paquetes_total % 2
    p_der = paquetes_total // 2

    # -----------------------
    # VISUALIZACIÓN DE RESULTADOS
    # -----------------------
    col_visual, col_tabla = st.columns([3, 1])

    with col_visual:
        st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)
        
        # Etiquetas de columnas
        lab1, lab2, lab3, lab4 = st.columns([1,1,1,1])
        lab1.caption("Saldos Izq")
        lab2.caption("Paquetes (130)")
        lab3.caption("Paquetes (130)")
        lab4.caption("Saldos Der")

        # Dibujar las 10 filas de la mula
        for i in range(10):
            r1, r2, r3, r4 = st.columns([1, 1, 1, 1])
            
            with r1:
                val = s_izq[i] if i < len(s_izq) else ""
                st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)
            with r2:
                val = PAQUETE if i < p_izq else ""
                st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
            with r3:
                val = PAQUETE if i < p_der else ""
                st.markdown(f'<div class="celda">{val}</div>', unsafe_allow_html=True)
            with r4:
                val = s_der[i] if i < len(s_der) else ""
                st.markdown(f'<div class="saldo">{val}</div>', unsafe_allow_html=True)

    with col_tabla:
        st.subheader("Resumen Teja #4")
        st.table({
            "Detalle": ["Cant. Pedida", "Paquetes", "Total Saldos", "Espacio Libre"],
            "Valor": [f"{cantidad}", f"{paquetes_total}", f"{len(lista_saldos)}", f"{CAPACIDAD_TOTAL - cantidad}"]
        })
        st.success("Distribución optimizada lista.")
else:
    st.warning("Esperando ingreso de cantidad en el panel lateral...")
