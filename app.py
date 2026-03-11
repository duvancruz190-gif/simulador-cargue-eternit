# ... (mantienes tu login y CSS igual)

# 4. LÓGICA DE CARGA OPTIMIZADA
with st.sidebar:
    st.header("📦 Entrada de Datos")
    # Usamos number_input para evitar errores de conversión de texto a int
    cantidad = st.number_input("Cantidad de Teja #4", min_value=0, step=1, value=0)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

# Constantes
PAQUETE = 130
MAX_PAQUETES = 20
MAX_SALDO_UNIDAD = 60
CAPACIDAD_TOTAL = (MAX_PAQUETES * PAQUETE) + (20 * MAX_SALDO_UNIDAD)

if cantidad > CAPACIDAD_TOTAL:
    st.error(f"⚠️ El pedido ({cantidad}) excede la capacidad máxima de {CAPACIDAD_TOTAL} unidades.")
    st.stop()

# Cálculos
paquetes_totales = cantidad // PAQUETE
sobrante_total = cantidad % PAQUETE

# Distribuir sobrante en unidades de máximo 60
saldos_lista = []
temp_sobrante = sobrante_total
while temp_sobrante > 0:
    carga = min(temp_sobrante, MAX_SALDO_UNIDAD)
    saldos_lista.append(carga)
    temp_sobrante -= carga

# Separación para las 4 columnas del camión
s_izq = saldos_lista[::2]  # Pares
s_der = saldos_lista[1::2] # Impares
p_izq = (paquetes_totales + 1) // 2
p_der = paquetes_totales // 2

# 5. RENDERIZADO DEL CAMIÓN
st.markdown('<div class="cabina">FRENTE DEL VEHÍCULO (CABINA)</div>', unsafe_allow_html=True)

# Creamos las filas (máximo 10 filas para representar el largo del camión)
for i in range(10):
    cols = st.columns([1, 1, 1, 1])
    
    # Datos de las 4 columnas: Saldo Izq | Paquete Izq | Paquete Der | Saldo Der
    datos_fila = [
        (s_izq[i] if i < len(s_izq) else "", "saldo"),
        (PAQUETE if i < p_izq else "", "celda"),
        (PAQUETE if i < p_der else "", "celda"),
        (s_der[i] if i < len(s_der) else "", "saldo")
    ]
    
    for col, (valor, estilo) in zip(cols, datos_fila):
        with col:
            if valor != "":
                st.markdown(f'<div class="{estilo}">{valor}</div>', unsafe_allow_html=True)
            else:
                # Espacio vacío estético
                st.markdown('<div style="height: 45px;"></div>', unsafe_allow_html=True)
