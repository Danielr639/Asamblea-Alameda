import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# 1. Configuración de página
st.set_page_config(
    page_title="Asamblea Alameda 7",
    page_icon="🏢",
    layout="centered"
)

# 2. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Listado de Preguntas Oficiales
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

# --- CABECERA PERSONALIZADA ---
# Verifica si el archivo existe (ajusta el nombre si es .jpg o .png)
logo_path = "image_f94506.jpg" 

if os.path.exists(logo_path):
    st.image(logo_path, use_container_width=True)
else:
    st.title("🏢 Asamblea Alameda 7")
    st.info("Nota: Sube la imagen 'image_f94506.jpg' a GitHub para ver el logo.")

st.divider()

# --- NAVEGACIÓN ---
rol = st.sidebar.radio("Menú de Acceso:", ["Copropietario", "Administrador"])

# --- VISTA ADMINISTRADOR ---
if rol == "Administrador":
    st.header("👨‍💼 Panel de Control")
    # NUEVA CONTRASEÑA PERSONALIZADA
    clave = st.text_input("Ingrese Contraseña de Administrador:", type="password")
    
    if clave == "Alameda2026*": 
        st.success("Acceso Autorizado")
        
        idx = st.selectbox("Seleccione Pregunta a Activar:", range(len(preguntas)), format_func=lambda x: preguntas[x])
        publicar_res = st.checkbox("Publicar resultados (Gráficos) a los vecinos")
        
        if st.button("📢 LANZAR PREGUNTA AHORA", use_container_width=True):
            df_status = pd.DataFrame({"id_pregunta": [idx], "ver_grafica": [str(publicar_res)]})
            conn.update(worksheet="Control", data=df_status)
            st.toast("¡Pregunta actualizada en la nube!")

# --- VISTA VOTANTE (Copropietario) ---
else:
    try:
        df_status = conn.read(worksheet="Control", ttl=1)
        p_activa = int(df_status.iloc[0, 0])
        mostrar_grafico = str(df_status.iloc[0, 1]) == "True"
    except:
        p_activa = -1

    if p_activa == -1:
        st.warning("⏳ La asamblea aún no ha iniciado. Por favor, espere instrucciones.")
        if st.button("🔄 Refrescar"): st.rerun()
    else:
        st.subheader(f"Pregunta Actual: {p_activa + 1}")
        st.markdown(f"### {preguntas[p_activa]}")
        
        casa = st.text_input("🏠 Número de Casa (1-184):", placeholder="Ejemplo: 12").strip()
        
        if casa:
            # Validación de duplicados
            df_votos = conn.read(worksheet="Votos", ttl=0)
            ya_voto = not df_votos[(df_votos['casa'].astype(str) == casa) & 
                                   (df_votos['pregunta'] == preguntas[p_activa])].empty
            
            if mostrar_grafico:
                st.success("📊 Votación cerrada. Resultados actuales:")
                resumen = df_votos[df_votos['pregunta'] == preguntas[p_activa]]['voto'].value_counts()
                st.bar_chart(resumen)
            
            elif ya_voto:
                st.error(f"La casa {casa} ya votó en esta ronda. Espere a la siguiente pregunta.")
            
            else:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ SÍ", use_container_width=True):
                        nuevo = pd.DataFrame([{"casa": casa, "pregunta": preguntas[p_activa], "voto": "SÍ"}])
                        df_act = pd.concat([df_votos, nuevo], ignore_index=True)
                        conn.update(worksheet="Votos", data=df_act)
                        st.balloons()
                        st.rerun()
                with c2:
                    if st.button("❌ NO", use_container_width=True):
                        nuevo = pd.DataFrame([{"casa": casa, "pregunta": preguntas[p_activa], "voto": "NO"}])
                        df_act = pd.concat([df_votos, nuevo], ignore_index=True)
                        conn.update(worksheet="Votos", data=df_act)
                        st.rerun()
