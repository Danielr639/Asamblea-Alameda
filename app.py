import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asamblea Alameda 7", page_icon="🏢")

# --- MEMORIA COMPARTIDA (Sincronización Real entre dispositivos) ---
@st.cache_resource
def obtener_memoria_comun():
    # Esta estructura vive en el servidor y todos los usuarios la comparten
    return {
        "pregunta_activa": 0,
        "mostrar_resultados": False,
        "votos_globales": pd.DataFrame(columns=["casa", "pregunta_id", "voto"])
    }

memoria = obtener_memoria_comun()

# --- DATOS ---
preguntas = [
    "1. ¿Aprueba la elección del Consejo de Administración por planchas?",
    "2. ¿Aprueba la elección del Comité de Convivencia por planchas?",
    "3. ¿Autoriza la pintura de la fachada de ladrillo?",
    "4. ¿Está de acuerdo con la 'cerca viva'?",
    "5. ¿Aprueba el nuevo Manual de Convivencia?",
    "6. ¿Aprueba el decomiso preventivo de objetos?",
    "7. ¿Aprueba cuota extraordinaria para canales?",
    "8. ¿Acuerda el encerramiento de la malla del parqueadero?"
]

# --- LOGO ---
logo_path = "image_f94506.jpg"
if os.path.exists(logo_path):
    st.image(logo_path, use_container_width=True)

st.divider()

# --- NAVEGACIÓN ---
rol = st.sidebar.radio("MENÚ", ["Votante", "Administrador"])

# --- MODO ADMINISTRADOR ---
if rol == "Administrador":
    st.header("👨‍💼 Panel de Mando")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "Alameda2026*":
        st.subheader("Control de Preguntas")
        
        # Selector de pregunta
        nueva_p = st.selectbox("Seleccione Pregunta para lanzar:", 
                               range(len(preguntas)), 
                               index=memoria["pregunta_activa"],
                               format_func=lambda x: preguntas[x])
        
        # Interruptor de resultados
        ver_res = st.toggle("Publicar Gráficos de Resultados", value=memoria["mostrar_resultados"])
        
        if st.button("🚀 ACTUALIZAR ASAMBLEA (Sincronizar todos los celulares)", type="primary"):
            memoria["pregunta_activa"] = nueva_p
            memoria["mostrar_resultados"] = ver_res
            st.success(f"Sincronizado: Pregunta {nueva_p + 1} activa.")
            st.rerun()

        st.divider()
        st.subheader("📊 Consolidado de Votos")
        st.dataframe(memoria["votos_globales"])
        
        if not memoria["votos_globales"].empty:
            csv = memoria["votos_globales"].to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Reporte Excel", data=csv, file_name="votos_alameda7.csv")

# --- MODO VOTANTE ---
else:
    # 1. Identificación de Casa (Se guarda en el navegador del vecino)
    if 'casa_id' not in st.session_state:
        st.subheader("Bienvenido")
        id_input = st.text_input("🏠 Ingrese su Número de Casa:").strip()
        if st.button("Entrar a Votar"):
            if id_input:
                st.session_state.casa_id = id_input
                st.rerun()
    else:
        casa = st.session_state.casa_id
        p_id = memoria["pregunta_activa"]
        
        st.sidebar.info(f"Casa: {casa}")
        if st.sidebar.button("Cerrar Sesión"):
            del st.session_state.casa_id
            st.rerun()

        # 2. Mostrar Pregunta Actual
        st.subheader(f"Pregunta {p_id + 1}")
        st.info(preguntas[p_id])

        # 3. Lógica de Votación
        df_votos = memoria["votos_globales"]
        # Filtramos para ver si ESTA casa ya votó en ESTA pregunta específica
        ya_voto = not df_votos[(df_votos['casa'] == casa) & (df_votos['pregunta_id'] == p_id)].empty

        if memoria["mostrar_resultados"]:
            st.success("📊 Resultados en Tiempo Real")
            conteo = df_votos[df_votos['pregunta_id'] == p_id]['voto'].value_counts()
            if not conteo.empty:
                st.bar_chart(conteo)
            else:
                st.write("Aún no hay votos en esta pregunta.")
            if st.button("🔄 Actualizar Gráfico"): st.rerun()

        elif ya_voto:
            st.warning("✅ Voto registrado. Espere a que el administrador lance la siguiente pregunta.")
            if st.button("🔄 Buscar Nueva Pregunta"): st.rerun()

        else:
            st.write("Seleccione su respuesta:")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("👍 SÍ", use_container_width=True):
                    nuevo_voto = pd.DataFrame([{"casa": casa, "pregunta_id": p_id, "voto": "SÍ"}])
                    memoria["votos_globales"] = pd.concat([memoria["votos_globales"], nuevo_voto], ignore_index=True)
                    st.balloons()
                    st.rerun()
            with c2:
                if st.button("👎 NO", use_container_width=True):
                    nuevo_voto = pd.DataFrame([{"casa": casa, "pregunta_id": p_id, "voto": "NO"}])
                    memoria["votos_globales"] = pd.concat([memoria["votos_globales"], nuevo_voto], ignore_index=True)
                    st.rerun()
