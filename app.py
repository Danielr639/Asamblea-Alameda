import streamlit as st
import pandas as pd
import os

# 1. Configuración de pantalla
st.set_page_config(page_title="Asamblea Alameda 7", page_icon="🏢")

# 2. Inicializar la "Base de Datos" interna en la memoria del servidor
if 'db_votos' not in st.session_state:
    st.session_state.db_votos = pd.DataFrame(columns=["casa", "pregunta", "voto"])

if 'p_activa' not in st.session_state:
    st.session_state.p_activa = 0

if 'ver_resultados' not in st.session_state:
    st.session_state.ver_resultados = False

# --- PREGUNTAS ---
preguntas = [
    "1. ¿Aprueba la elección del Consejo de Administración por planchas?",
    "2. ¿Aprueba la elección del Comité de Convivencia por planchas?",
    "3. ¿Autoriza la pintura de la fachada de ladrillo (sujeto a recursos)?",
    "4. ¿Está de acuerdo con la 'cerca viva' entre etapas (sujeto a recursos)?",
    "5. ¿Aprueba el contenido del nuevo Manual de Convivencia?",
    "6. ¿Aprueba el decomiso preventivo de objetos en zonas comunes?",
    "7. ¿Aprueba la cuota extraordinaria para canales de desagüe?",
    "8. ¿Acuerda el encerramiento de la malla del parqueadero?"
]

# --- CABECERA CON LOGO ---
logo_path = "image_f94506.jpg"
if os.path.exists(logo_path):
    st.image(logo_path, use_container_width=True)
else:
    st.title("🏢 Asamblea Alameda 7")

st.divider()

# --- NAVEGACIÓN ---
rol = st.sidebar.radio("Menú:", ["Votante", "Administrador"])

# --- VISTA ADMINISTRADOR ---
if rol == "Administrador":
    st.header("👨‍💼 Panel de Control")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "Alameda2026*":
        st.success("Control Maestro Activado")
        
        # Control de Preguntas
        st.session_state.p_activa = st.selectbox("Seleccionar Pregunta:", range(len(preguntas)), format_func=lambda x: preguntas[x])
        st.session_state.ver_resultados = st.checkbox("Publicar Gráficos a los Vecinos", value=st.session_state.ver_resultados)
        
        st.divider()
        st.subheader("📥 Descargar Reporte Final")
        if not st.session_state.db_votos.empty:
            csv = st.session_state.db_votos.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Descargar Excel (CSV) de Votos", data=csv, file_name="votos_alameda_7.csv", mime="text/csv")
            
            st.write("Vista previa de votos recibidos:")
            st.dataframe(st.session_state.db_votos.tail(5)) # Muestra los últimos 5
        else:
            st.info("Aún no hay votos registrados.")

# --- VISTA VOTANTE ---
else:
    p_idx = st.session_state.p_activa
    st.subheader(f"Pregunta {p_idx + 1}")
    st.markdown(f"### {preguntas[p_idx]}")
    
    casa = st.text_input("🏠 Su Número de Casa:", placeholder="Ej: 10").strip()
    
    if casa:
        # Verificar si esta casa ya votó en LA PREGUNTA ACTUAL
        df = st.session_state.db_votos
        ya_voto = not df[(df['casa'] == casa) & (df['pregunta'] == preguntas[p_idx])].empty
        
        if st.session_state.ver_resultados:
            st.success("📊 Votación Cerrada. Resultados:")
            conteo = df[df['pregunta'] == preguntas[p_idx]]['voto'].value_counts()
            if not conteo.empty:
                st.bar_chart(conteo)
            else:
                st.write("No hubo votos en esta pregunta.")
        
        elif ya_voto:
            st.error(f"La casa {casa} ya votó. Por favor, espere la siguiente pregunta.")
        
        else:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ SÍ", use_container_width=True):
                    nuevo_voto = pd.DataFrame([{"casa": casa, "pregunta": preguntas[p_idx], "voto": "SÍ"}])
                    st.session_state.db_votos = pd.concat([st.session_state.db_votos, nuevo_voto], ignore_index=True)
                    st.balloons()
                    st.rerun()
            with c2:
                if st.button("❌ NO", use_container_width=True):
                    nuevo_voto = pd.DataFrame([{"casa": casa, "pregunta": preguntas[p_idx], "voto": "NO"}])
                    st.session_state.db_votos = pd.concat([st.session_state.db_votos, nuevo_voto], ignore_index=True)
                    st.rerun()
