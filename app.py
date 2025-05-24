import streamlit as st
from supabase import create_client, Client
import random
import uuid
import json
import pandas as pd

# --- Configuración de Supabase (¡Desde secrets.toml!) ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Funciones de Generación de Preguntas Personalizadas ---

def generar_pregunta_personalizada(template_id, clave):
    """
    Genera una pregunta aritmética personalizada usando la clave directamente en la operación.
    Retorna un diccionario con 'pregunta', 'respuesta_correcta', y 'id_pregunta_en_hoja'.
    """
    # Asegúrate de que la clave sea un número para las operaciones
    if not isinstance(clave, int) or clave <= 0:
        # Esto debería manejarse en la entrada de la clave, pero es una salvaguarda
        clave = 1 # Valor por defecto si la clave no es válida

    # Usamos la clave directamente o derivadas simples de ella para los operandos
    val_clave = clave
    val_doble_clave = clave * 2
    val_mitad_clave = clave // 2 if clave % 2 == 0 else clave + 1 # Asegura que sea entero para división
    val_mas_cinco = clave + 5
    val_por_tres = clave * 3

    # Definir las plantillas de preguntas y calcular respuestas
    if template_id == "suma_clave":
        num2 = random.randint(1, 10) # Otro número aleatorio para variar la suma
        pregunta = f"¿Cuánto es {val_clave} + {num2}?"
        respuesta_correcta = str(val_clave + num2)
    elif template_id == "resta_clave":
        num_restar = random.randint(1, val_clave // 2) # Aseguramos que la resta no dé negativo
        if val_clave - num_restar <= 0: num_restar = 1 # Evitar 0 o negativos si clave es muy pequeña
        pregunta = f"¿Cuánto es {val_clave} - {num_restar}?"
        respuesta_correcta = str(val_clave - num_restar)
    elif template_id == "multiplicacion_clave":
        num_multiplicar = random.randint(2, 5) # Multiplicar por un número pequeño
        pregunta = f"¿Cuánto es {val_clave} * {num_multiplicar}?"
        respuesta_correcta = str(val_clave * num_multiplicar)
    elif template_id == "division_clave":
        # Aseguramos una división exacta con la clave
        multiplicador = random.randint(2, 5)
        dividendo = val_clave * multiplicador
        pregunta = f"¿Cuánto es {dividendo} / {val_clave}?"
        respuesta_correcta = str(multiplicador) # La respuesta siempre será el multiplicador
    elif template_id == "operacion_mixta_clave":
        num1 = val_clave + random.randint(1, 3)
        num2 = val_clave - random.randint(0, min(val_clave -1, 3)) # No restar más de lo que tiene
        if num2 <= 0: num2 = 1
        pregunta = f"¿Cuánto es ({num1} * {num2}) - {val_clave}?"
        respuesta_correcta = str((num1 * num2) - val_clave)
    else:
        pregunta = f"Pregunta no definida para template {template_id}."
        respuesta_correcta = ""
    
    # Generar un ID único para la pregunta dentro de la hoja
    id_pregunta_unica = f"q_{template_id}_{uuid.uuid4().hex[:4]}" # Usamos UUID para asegurar unicidad si la misma template se usa varias veces

    return {
        "id": template_id, # ID del tipo de pregunta
        "pregunta": pregunta,
        "respuesta_correcta": respuesta_correcta,
        "id_pregunta_en_hoja": id_pregunta_unica # ID único para esta instancia de pregunta
    }

# --- Funciones de Generación de Hojas de Trabajo ---
def generar_hoja_personalizada_con_clave(hoja_numero, clave_alumno_int, num_preguntas_por_hoja=5):
    """
    Genera una hoja de trabajo completa con 5 preguntas personalizadas
    basadas en la clave entera del alumno, con 5 preguntas fijas.
    """
    # Definimos 5 tipos de preguntas (templates) que queremos en cada hoja
    # Estas son las que se repetirán, pero con valores personalizados por la clave.
    template_ids_fijos = [
        "suma_clave",
        "resta_clave",
        "multiplicacion_clave",
        "division_clave",
        "operacion_mixta_clave"
    ]
    
    # Aseguramos que tengamos 5 preguntas si num_preguntas_por_hoja lo pide.
    # Si quieres que haya aleatoriedad en los *tipos* de preguntas, puedes usar random.sample
    # de un pool más grande de templates, pero si quieres 5 fijas, así está bien.
    
    preguntas_personalizadas = []
    # Aseguramos que siempre haya 5 preguntas usando estos templates fijos
    for i in range(num_preguntas_por_hoja):
        if i < len(template_ids_fijos):
            pregunta = generar_pregunta_personalizada(template_ids_fijos[i], clave_alumno_int)
            # Aseguramos que el ID de la pregunta sea único por hoja para el manejo de respuestas
            pregunta["id_pregunta_en_hoja"] = f"hoja_{hoja_numero}_q_{i+1}_{template_ids_fijos[i]}"
            preguntas_personalizadas.append(pregunta)
        else:
            # Si se piden más de 5 preguntas, puedes repetir templates o añadir más en template_ids_fijos
            break # Por ahora, nos quedamos con las 5 definidas

    hoja_id_unica = f"hoja_{hoja_numero+1}_clave_{clave_alumno_int}"
    return {"id": hoja_id_unica, "preguntas": preguntas_personalizadas}


def generar_todas_las_hojas_por_clave(clave_alumno_int, num_hojas=5, num_preguntas_por_hoja=5):
    """Genera un conjunto de X hojas de trabajo personalizadas para una clave dada."""
    # Validación de la clave antes de generar
    if not isinstance(clave_alumno_int, int) or clave_alumno_int <= 0:
        st.error("La clave de personalización debe ser un número entero positivo para generar hojas.")
        return []

    hojas_generadas = []
    # Usamos random.seed para que la selección de preguntas sea consistente
    # si decidimos hacer una selección aleatoria de templates en el futuro.
    # Por ahora, como tenemos 5 templates fijos, no es tan crítico aquí.
    # random.seed(clave_alumno_int) 

    for i in range(num_hojas):
        hojas_generadas.append(generar_hoja_personalizada_con_clave(i, clave_alumno_int, num_preguntas_por_hoja))
    return hojas_generadas

# --- Funciones de Evaluación y Guardado de Nota (Ligeramente ajustadas para float/int) ---
def evaluar_y_guardar_nota(respuestas_alumno, hoja_data, alumno_id_final):
    """Evalúa las respuestas del alumno y guarda la nota en Supabase."""
    nota_correctas = 0
    respuestas_detalladas = {}
    total_preguntas = len(hoja_data["preguntas"])
    
    for pregunta_info in hoja_data["preguntas"]:
        pregunta_id_en_hoja = pregunta_info["id_pregunta_en_hoja"] 
        respuesta_correcta_str = str(pregunta_info["respuesta_correcta"]).lower().strip()
        respuesta_alumno_str = str(respuestas_alumno.get(pregunta_id_en_hoja, "")).lower().strip()

        es_correcta = False
        try:
            # Intentar convertir ambas a flotantes para comparación numérica, si aplica
            num_correcta = float(respuesta_correcta_str)
            num_alumno = float(respuesta_alumno_str)
            # Comparar con una pequeña tolerancia para flotantes
            if abs(num_correcta - num_alumno) < 0.001: 
                es_correcta = True
        except ValueError:
            # Si no son números, comparar como strings directamente
            if respuesta_alumno_str == respuesta_correcta_str:
                es_correcta = True
        
        respuestas_detalladas[pregunta_id_en_hoja] = {
            "pregunta": pregunta_info["pregunta"],
            "respuesta_alumno": respuestas_alumno.get(pregunta_id_en_hoja),
            "respuesta_correcta": pregunta_info["respuesta_correcta"],
            "es_correcta": es_correcta
        }
        
        if es_correcta:
            nota_correctas += 1

    if total_preguntas > 0:
        nota_final = (nota_correctas / total_preguntas) * 100
    else:
        nota_final = 0

    st.session_state['last_score'] = nota_final

    data_to_insert = {
        "alumno_id": alumno_id_final,
        "hoja_id": hoja_data["id"],
        "nota": round(nota_final, 2),
        "respuestas_alumno": json.dumps(respuestas_detalladas)
    }

    try:
        response = supabase.table("notas_hojas_trabajo").insert([data_to_insert]).execute()
        if response.data:
            st.success(f"¡Nota {round(nota_final, 2)}% guardada automáticamente para {alumno_id_final} en {hoja_data['id']}!")
            st.balloons()
            # Reiniciar el estado para nueva interacción o elección
            st.session_state['selected_hoja'] = None
            st.session_state['current_hoja_display'] = None
            st.session_state['respuestas'] = {}
            st.session_state['hojas_disponibles'] = [] # Forzar regeneración si se ingresa nueva clave
            st.cache_data.clear() # Limpiar caché de notas para recargar la tabla del maestro
            st.experimental_rerun()
        else:
            st.error(f"Error al guardar la nota: {response.data}")

    except Exception as e:
        st.error(f"Error de conexión a Supabase al guardar la nota: {e}")

# --- Interfaz de Usuario de Streamlit ---
st.set_page_config(layout="centered", page_title="Generador de Hojas de Trabajo Personalizadas")
st.title("📝 Hojas de Trabajo Aritméticas Personalizadas")
st.markdown("Ingresa tu clave para generar tus hojas de trabajo y tu nota se guardará automáticamente.")

# Sección de Entrada de Clave (ID de Alumno/Personalización)
st.header("1. Ingresa tu Clave de Personalización")
clave_input_str = st.text_input(
    "Ingresa tu clave (un número entero, ej. 5, 12, 100):",
    key="clave_personalizacion_input"
)

# Validar la clave y convertirla a entero si es posible
clave_personalizacion_int = None # Esta será la clave numérica que usaremos
if clave_input_str.strip():
    try:
        clave_personalizacion_int = int(clave_input_str.strip())
        if clave_personalizacion_int <= 0:
            st.error("La clave debe ser un número entero positivo.")
            clave_personalizacion_int = None
    except ValueError:
        st.error("La clave debe ser un número entero válido.")
        clave_personalizacion_int = None
else:
    st.info("Por favor, ingresa tu clave para generar las hojas de trabajo.")


# --- Estado de la Aplicación (Manejo de la clave y regeneración) ---
# Regenerar hojas si la clave ha cambiado o si no hay hojas
if clave_personalizacion_int is not None and (
    'current_personalization_key' not in st.session_state or
    st.session_state['current_personalization_key'] != clave_personalizacion_int or
    not st.session_state.get('hojas_disponibles')
):
    st.session_state['current_personalization_key'] = clave_personalizacion_int
    st.session_state['hojas_disponibles'] = generar_todas_las_hojas_por_clave(clave_personalizacion_int, num_hojas=5, num_preguntas_por_hoja=5)
    st.session_state['selected_hoja'] = None
    st.session_state['current_hoja_display'] = None
    st.session_state['respuestas'] = {}
    st.experimental_rerun()

# --- Sección de Selección de Hoja de Trabajo ---
if clave_personalizacion_int is not None and st.session_state['current_hoja_display'] is None:
    st.header("2. Elige una Hoja de Trabajo")
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]

    if st.session_state.get('hojas_disponibles'):
        for i, hoja in enumerate(st.session_state['hojas_disponibles']):
            with cols[i]:
                if st.button(f"Hoja {i+1}", key=f"select_hoja_{hoja['id']}"):
                    st.session_state['selected_hoja'] = hoja['id']
                    st.session_state['current_hoja_display'] = hoja
                    st.session_state['respuestas'] = {q['id_pregunta_en_hoja']: "" for q in hoja['preguntas']}
                    st.experimental_rerun()
    else:
        st.info("Ingresa una clave válida para generar las hojas.")
elif clave_personalizacion_int is None:
    st.info("Ingresa una clave para ver las hojas de trabajo.")


# --- Sección de Presentación de la Hoja de Trabajo ---
if st.session_state['current_hoja_display'] is not None and clave_personalizacion_int is not None:
    st.header(f"3. Hoja de Trabajo: {st.session_state['current_hoja_display']['id']}")
    st.write(f"¡Hola, {clave_input_str}! Resuelve las siguientes preguntas:")

    with st.form(key=f"examen_form_{st.session_state['current_hoja_display']['id']}"):
        for i, pregunta_info in enumerate(st.session_state['current_hoja_display']["preguntas"]):
            st.subheader(f"Pregunta {i+1}:")
            st.markdown(f"**{pregunta_info['pregunta']}**")

            st.session_state['respuestas'][pregunta_info["id_pregunta_en_hoja"]] = st.text_input(
                f"Tu respuesta para la pregunta {i+1}:",
                value=st.session_state['respuestas'].get(pregunta_info["id_pregunta_en_hoja"], ""),
                key=f"ans_{st.session_state['current_hoja_display']['id']}_{pregunta_info['id_pregunta_en_hoja']}"
            )

        submit_button = st.form_submit_button("Terminar Examen y Guardar Nota")

        if submit_button:
            if not clave_input_str.strip() or clave_personalizacion_int is None:
                st.warning("Por favor, ingresa una clave válida antes de terminar el examen.")
            else:
                evaluar_y_guardar_nota(
                    st.session_state['respuestas'],
                    st.session_state['current_hoja_display'],
                    clave_input_str # Guardamos la clave original como el alumno_id
                )

if 'last_score' in st.session_state and st.session_state['selected_hoja'] is None and clave_personalizacion_int is not None:
    st.info(f"Tu última nota obtenida fue: **{st.session_state['last_score']:.2f}%**")


st.markdown("---")

# Sección para el Maestro: Ver todas las notas guardadas
st.header("📊 Registro de Notas (Maestro)")

@st.cache_data(ttl=60)
def get_all_notes():
    try:
        response = supabase.table("notas_hojas_trabajo").select("*").order("created_at", desc=True).limit(20).execute()
        return response.data
    except Exception as e:
        st.error(f"Error al cargar las notas: {e}")
        return None

notes_data = get_all_notes()

if notes_data:
    df_notes = pd.DataFrame(notes_data)
    df_notes.rename(columns={'created_at': 'Fecha y Hora', 'alumno_id': 'ID Alumno', 'hoja_id': 'ID Hoja', 'nota': 'Nota (%)'}, inplace=True)
    st.dataframe(df_notes[['Fecha y Hora', 'ID Alumno', 'ID Hoja', 'Nota (%)']])
else:
    st.info("Aún no hay notas guardadas en la base de datos.")

st.markdown("---")
st.caption("Aplicación desarrollada con Streamlit y Supabase.")