import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="Asamblea Alameda 7 PRO", 
    page_icon="🏢", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

# --- 2. MEMORIA GLOBAL ---
@st.cache_resource
def iniciar_servidor():
    return {
        "asamblea_iniciada": False,
        "fase": "espera", 
        "p_idx": 0,
        "votos": pd.DataFrame(columns=["casa", "representa", "p_id", "voto"]),
        "conectados": {}, 
        "tiempo_cierre": None
    }

servidor = iniciar_servidor()
TOTAL_CASAS = 184

# --- 3. NAVEGACIÓN LATERAL ---
rol = st.sidebar.radio("SISTEMA DE ASAMBLEA", ["Votante", "Administrador"], key="nav_main")

# --- 4. CSS DIFERENCIADO POR ROL ---
if rol == "Votante":
    # OCULTA TODO PARA EL VOTANTE
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        header {visibility: hidden !important;}
        .stDeployButton {display:none !important;}
        #manage-app-button {display:none !important;}
        [data-testid="stHeader"] {display:none !important;}
        </style>
        """, unsafe_allow_html=True)
else:
    # EL ADMIN SÍ VE EL MENÚ (Por si necesita opciones de Streamlit)
    st.markdown("""
        <style>
        footer {visibility: hidden !important;}
        .stDeployButton {display:none !important;}
        </style>
        """, unsafe_allow_html=True)

# --- 5. LOGO ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if os.path.exists("image_f94506.jpg"):
        st.image("image_f94506.jpg", width=200)
    else:
        st.title("🏢 Alameda 7")

st.divider()

# --- VISTA ADMINISTRADOR ---
if rol == "Administrador":
    st.header("👨‍💼 Panel de Mando (Admin)")
    clave = st.text_input("Contraseña Maestro:", type="password", key="admin_key")
    
    if clave == "Alameda2026*":
        # MONITOR DE ASISTENCIA
        casas_presentes = sum(servidor["conectados"].values())
        porcentaje_quorum = (casas_presentes / TOTAL_CASAS) * 100
        st.subheader(f"📊 Quórum: {porcentaje_quorum:.1f}% ({casas_presentes} casas)")
        st.progress(min(porcentaje_quorum / 100, 1.0))
        
        # MENÚ DE MANTENIMIENTO (NUEVO)
        with st.sidebar.expander("🛠️ HERRAMIENTAS DE SISTEMA"):
            if st.button("🧹 LIMPIAR TODA LA DATA (RESET)", use_container_width=True):
                servidor["votos"] = pd.DataFrame(columns=["casa", "representa", "p_id", "voto"])
                servidor["conectados"] = {}
                servidor["asamblea_iniciada"] = False
                servidor["fase"] = "espera"
                st.success("Sistema reiniciado")
                st.rerun()
            
            if st.button("🔄 REFRESCAR SERVIDOR", use_container_width=True):
                st.rerun()

        if not servidor["asamblea_iniciada"]:
            if st.button("🚀 INICIAR ASAMBLEA", type="primary", use_container_width=True):
                servidor["asamblea_iniciada"] = True
                st.rerun()
        else:
            # GESTIÓN DE PREGUNTAS
            preguntas = [f"{i+1}. Pregunta..." for i in range(10)] # Simplificado para el ejemplo de carga
            # Lista Real
            preguntas_lista = [
                "1. ¿Aprueba la elección del Consejo de Administración por planchas?",
                "2. ¿Aprueba la elección del Comité de Convivencia por planchas?",
                "3. ¿Autoriza la pintura de la fachada de ladrillo?",
                "4. ¿Está de acuerdo con la 'cerca viva' entre etapas?",
                "5. ¿Aprueba el nuevo Manual de Convivencia?",
                "6. ¿Aprueba el decomiso preventivo de objetos?",
                "7. ¿Aprueba la cuota extraordinaria de desagüe?",
                "8. ¿Acuerda el encerramiento de la malla?",
                "9. ¿Cuál cuota de administración prefiere? (70k, 75k, 85k)",
                "10. ¿Aprueban la App para la votación en Alameda 7?"
            ]
            
            sel_p = st.selectbox("Seleccione Pregunta:", range(len(preguntas_lista)), 
                                 index=servidor['p_idx'], format_func=lambda x: preguntas_lista[x])
            
            segundos = st.slider("Tiempo (Seg):", 30, 300, 60)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📢 LANZAR PREGUNTA", type="primary", use_container_width=True):
                    servidor['p_idx'] = sel_p
                    servidor['fase'] = "votacion"
                    servidor['tiempo_cierre'] = datetime.now() + timedelta(seconds=segundos)
                    st.rerun()
            with c2:
                if st.button("📊 VER RESULTADOS", use_container_width=True):
                    servidor['fase'] = "resultados"
                    st.rerun()

            # MONITOR
            df_v = servidor['votos']
            v_act = df_v[df_v['p_id'] == sel_p]
            if not v_act.empty:
                res_sum = v_act.groupby('voto')['representa'].sum()
                fig, ax = plt.subplots(figsize=(5,3))
                # Colores fijos
                color_map = {'SÍ': '#2ecc71', 'NO': '#e74c3c', '70.000': '#2ecc71', '75.000': '#3498db', '85.000': '#e74c3c'}
                labels = res_sum.index.tolist()
                colors = [color_map.get(l, '#95a5a6') for l in labels]
                ax.pie(res_sum, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
                st.pyplot(fig)
                
                with st.expander("📋 Ver Planilla de Votos"):
                    st.dataframe(df_v)

            st.download_button("📥 Descargar Reporte Final", data=df_v.to_csv(index=False).encode('utf-8'), file_name="resultados.csv")

# --- VISTA VOTANTE ---
else:
    # Preguntas lista duplicada para el scope del votante
    preguntas_v = [
        "1. ¿Aprueba la elección del Consejo de Administración por planchas?",
        "2. ¿Aprueba la elección del Comité de Convivencia por planchas?",
        "3. ¿Autoriza la pintura de la fachada de ladrillo?",
        "4. ¿Está de acuerdo con la 'cerca viva' entre etapas?",
        "5. ¿Aprueba el nuevo Manual de Convivencia?",
        "6. ¿Aprueba el decomiso preventivo de objetos?",
        "7. ¿Aprueba la cuota extraordinaria de desagüe?",
        "8. ¿Acuerda el encerramiento de la malla?",
        "9. ¿Cuál cuota de administración prefiere?",
        "10. ¿Aprueban la App para la votación en Alameda 7?"
    ]
    
    if 'mi_casa' not in st.session_state:
        st.subheader("Registro de Ingreso")
        c_in = st.text_input("🏠 Número de Casa:", key="casa_v").strip()
        poderes = st.number_input("¿A cuántas casas representa?", 1, 10, 1, key="poder_v")
        if st.button("Entrar a Votar", type="primary", use_container_width=True):
            if c_in:
                st.session_state.mi_casa = c_in
                st.session_state.num_votos = poderes
                servidor['conectados'][c_in] = poderes
                st.rerun()
    else:
        casa, repre = st.session_state.mi_casa, st.session_state.num_votos
        st.sidebar.markdown(f"### 📋 Su Planilla\n**Casa Principal:** {casa}\n**Votos Totales:** {repre}")
        if st.sidebar.button("Cerrar Sesión"):
            del st.session_state.mi_casa
            st.rerun()

        if not servidor["asamblea_iniciada"]:
            st.warning("⏳ Esperando inicio de la Asamblea...")
            time.sleep(3); st.rerun()
        
        fase, p_id = servidor['fase'], servidor['p_idx']
        
        if fase == "espera":
            st.info("⌛ El administrador está preparando la pregunta...")
            time.sleep(3); st.rerun()
        else:
            # --- PREGUNTA FUENTE GIGANTE ---
            st.markdown(f"""
                <div style='text-align: center; padding: 10px;'>
                    <h1 style='font-size: 50px !important; font-weight: bold; color: #000000; line-height: 1.2;'>
                        {preguntas_v[p_id]}
                    </h1>
                </div>
                """, unsafe_allow_html=True)
            
            reloj_area = st.empty()
            df = servidor['votos']
            ya_voto = not df[(df['casa'] == casa) & (df['p_id'] == p_id)].empty
            
            res = (servidor['tiempo_cierre'] - datetime.now()).total_seconds() if fase == "votacion" and servidor['tiempo_cierre'] else 0

            if fase == "resultados":
                st.success("📊 RESULTADOS FINALES")
                v_p = df[df['p_id'] == p_id]
                if not v_p.empty:
                    res_s = v_p.groupby('voto')['representa'].sum()
                    fig, ax = plt.subplots()
                    color_map = {'SÍ': '#2ecc71', 'NO': '#e74c3c', '70.000': '#2ecc71', '75.000': '#3498db', '85.000': '#e74c3c'}
                    l = res_s.index.tolist(); c = [color_map.get(i, '#95a5a6') for i in l]
                    ax.pie(res_s, labels=l, autopct='%1.1f%%', colors=c)
                    st.pyplot(fig)
                st.button("🔄 Actualizar")

            elif ya_voto:
                st.success(f"✅ Voto registrado (Casa {casa}).")
                time.sleep(5); st.rerun()

            elif fase == "votacion" and res > 0:
                reloj_area.error(f"⏱️ CIERRE EN: {int(res)} segundos")
                # Pregunta 9 especial
                if p_id == 8:
                    for op in ["70.000", "75.000", "85.000"]:
                        if st.button(f"VOTAR: {op}", use_container_width=True, key=f"p9_{op}"):
                            servidor['votos'] = pd.concat([servidor['votos'], pd.DataFrame([{"casa": casa, "representa": repre, "p_id": p_id, "voto": op}])], ignore_index=True)
                            st.rerun()
                else: 
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ SÍ", use_container_width=True, key="btn_si"):
                            servidor['votos'] = pd.concat([servidor['votos'], pd.DataFrame([{"casa": casa, "representa": repre, "p_id": p_id, "voto": "SÍ"}])], ignore_index=True)
                            st.balloons(); st.rerun()
                    with c2:
                        if st.button("❌ NO", use_container_width=True, key="btn_no"):
                            servidor['votos'] = pd.concat([servidor['votos'], pd.DataFrame([{"casa": casa, "representa": repre, "p_id": p_id, "voto": "NO"}])], ignore_index=True)
                            st.rerun()
                time.sleep(1); st.rerun()
            else:
                st.warning("⌛ Tiempo terminado."); time.sleep(3); st.rerun()
