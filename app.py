import streamlit as st

# 1. CONFIGURACIÓN DE SEGURIDAD
USUARIO_CORRECTO = "DUVANCRUZ190@GMAIL.COM"
CLAVE_CORRECTA = "Du854872*"

st.set_page_config(page_title="Smart Picking & Logistic Guide", layout="wide")

# Función de Validación de Acceso
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
                <div style="background-color: #E0E0E0; padding: 30px; border-radius: 15px; border-top: 8px solid #E30613; text-align: center;">
                    <h1 style="color: #E30613; margin-bottom: 0; font-family: Arial Black;">ETERNIT</h1>
                    <p style="color: #1A3A5A; font-weight: bold;">SISTEMA DE PICKING</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Inicie sesión para continuar")
            usuario = st.text_input("Correo electrónico").upper()
            clave = st.text_input("Contraseña", type="password")
            
            if st.button("Ingresar"):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos")
        return False
    return True

if login():
    # 2. ESTILOS CSS (LOGOS, BARRA Y CAMIÓN)
    st.markdown("""
    <style>
        /* Contenedor blanco para el encabezado */
        .header-container {
            background-color: white;
            padding: 10px 0px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        /* Barra decorativa gris delgada con borde rojo inferior */
        .decor-bar {
            background-color: #EEEEEE; 
            border-bottom: 5px solid #E30613; 
            height: 30px; 
            width: 100%;
            border-radius: 5
