import streamlit as st
import pandas as pd
import json
import os

# Archivos de datos
DB_VOTOS = "votos.csv"
ESTADO_JSON = "estado_asamblea.json"

# Inicializar archivos base
if not os.path.exists(DB_VOTOS):
    pd.DataFrame(columns=["casa", "pregunta", "voto"]).to_csv(DB_VOTOS, index=False)

def cargar_estado():
    if os.path.exists(ESTADO_JSON):
        with open(ESTADO_JSON, "r") as f:
            return json.load(f)
    return {"pregunta_activa": -1, "mostrar_resultados": False}

def guardar_estado(estado):
    with open(ESTADO_JSON, "w") as f:
        json.dump(estado, f)

preguntas = [
    "1. ¿Aprueba la elección del Consejo de Administración por planchas?",
    "2. ¿Aprueba la elección del Comité de Convivencia por planchas?",
    "3. ¿Autoriza la pintura de la fachada (sujeto a recursos)?",
    "4. ¿Está de acuerdo con la 'cerca viva' entre etapas?",
    "5. ¿Aprueba el nuevo Manual de Convivencia?",
    "6. ¿Aprueba el decomiso preventivo de objetos en zonas comunes?",
    "7. ¿Aprueba cuota extraordinaria para canales de desagüe?",
    "8. ¿Acuerda el encerramiento de la malla del parqueadero?"
]

# --- INTERFAZ ---
st.sidebar.title("Menú de Acceso")
modo = st.sidebar.radio("Seleccione rol:", ["Votante", "Administrador"])
estado = cargar_estado()

# --- PANEL ADMINISTRADOR ---
if modo == "Administrador":
    st.title("👨‍💼 Control de la Asamblea")
    clave = st.text_input("Contraseña de seguridad", type="password")
    
    if clave == "admin2026": # Puedes cambiar esta clave
        st.info("Desde aquí controlas qué ven los 184 copropietarios.")
        
        idx = st.selectbox("Seleccionar pregunta:", range(len(preguntas)), format_func=lambda x: preguntas[x])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Lanzar Pregunta"):
                estado["pregunta_activa"] = idx
                estado["mostrar_resultados"] = False
                guardar_estado(estado)
                st.success("Pregunta lanzada")
        
        with col2:
            if st.button("📊 Mostrar Resultados"):
                estado["mostrar_resultados"] = True
                guardar_estado(estado)
        
        with col3:
            if st.button("⏹️ Cerrar Todo"):
                estado["pregunta_activa"] = -1
                guardar_estado(estado)
        
        # Monitor en tiempo real para el Admin
        st.divider()
        df = pd.read_csv(DB_VOTOS)
        votos_actuales = df[df['pregunta'] == preguntas[estado["pregunta_activa"]]]
        st.metric("Total votos recibidos en esta pregunta", len(votos_actuales))
        if not votos_actuales.empty:
            st.bar_chart(votos_actuales['voto'].value_counts())

# --- PANEL VOTANTE ---
else:
    st.title("🗳️ Votación en Línea")
    
    if estado["pregunta_activa"] == -1:
        st.warning("Asamblea en espera. El administrador aún no ha iniciado la pregunta.")
        if st.button("🔄 Refrescar"): st.rerun()
    
    else:
        pregunta_texto = preguntas[estado["pregunta_activa"]]
        st.subheader(f"Pregunta {estado['pregunta_activa'] + 1}")
        st.write(f"**{pregunta_texto}**")
        
        casa = st.text_input("Ingrese su número de casa (1-184):", placeholder="Ej: 45").strip()
        
        # Lógica de validación
        df_votos = pd.read_csv(DB_VOTOS)
        ya_voto = not df_votos[(df_votos['casa'].astype(str) == casa) & (df_votos['pregunta'] == pregunta_texto)].empty
        
        if estado["mostrar_resultados"]:
            st.info("Votación cerrada para esta pregunta. Visualizando resultados...")
            resumen = df_votos[df_votos['pregunta'] == pregunta_texto]['voto'].value_counts()
            st.bar_chart(resumen)
        
        elif ya_voto and casa != "":
            st.error(f"La casa {casa} ya registró su voto para esta pregunta.")
        
        else:
            col_si, col_no = st.columns(2)
            with col_si:
                if st.button("✅ SÍ", use_container_width=True, disabled=not casa):
                    nuevo = pd.DataFrame([{"casa": casa, "pregunta": pregunta_texto, "voto": "SÍ"}])
                    nuevo.to_csv(DB_VOTOS, mode='a', header=False, index=False)
                    st.balloons()
                    st.rerun()
            with col_no:
                if st.button("❌ NO", use_container_width=True, disabled=not casa):
                    nuevo = pd.DataFrame([{"casa": casa, "pregunta": pregunta_texto, "voto": "NO"}])
                    nuevo.to_csv(DB_VOTOS, mode='a', header=False, index=False)
                    st.rerun()