import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="App de Control de Ritmos e Intensidades",
    page_icon="🏃‍♂️",
    layout="wide",
)

file_path = "Calculadora_Ritmos_Atletas_BD.xlsx"


@st.cache_data(ttl=1)
def load_data():
  if os.path.exists(file_path):
    df_atletas = pd.read_excel(file_path, sheet_name="Registro Atletas")
    return df_atletas
  else:
    data = {
        "ID": [1, 2, 3, 4],
        "Nombre del Atleta": [
            "Atleta Velocidad 1",
            "Atleta Velocidad 2",
            "Atleta 400m",
            "Atleta 800m",
        ],
        "Categoría": ["Junior", "Junior", "Senior", "Senior"],
        "Especialidad": ["Velocista", "Velocista", "400m", "Medio Fondo"],
        "Prueba Base": ["100m", "200m", "400m", "800m"],
        "Marca Objetivo (s)": [11.5, 24.0, 51.5, 120.0],
        "Velocidad Media (m/s)": [8.695652, 8.333333, 7.766990, 6.666667],
    }
    return pd.DataFrame(data)


df_atletas = load_data()

st.title("🏃‍♂️ Sistema Avanzado de Control de Ritmos e Intensidades")
st.markdown(
    "Modelo biomecánico con control de aceleración inicial, tasas de fatiga y"
    " sistemas energéticos."
)

menu = st.sidebar.selectbox(
    "Menú de Navegación",
    [
        "📊 Perfil y Calculadora de Ritmos",
        "⚡ Calculadora por Distancia y Tiempo Objetivo",
        "➕ Registrar Nuevo Atleta",
        "✏️ Editar o Eliminar Atletas",
        "📈 Comparativa de Atletas",
    ],
)


def obtener_sistema_pausa(d):
  if d <= 50:
    return "P.A.A.L (0-6s)", "2.5-3 min", "6-8 min"
  elif d <= 100:
    return "C.A.A.L (7-10s)", "3-5 min", "6-8 min"
  elif d <= 250:
    return "P.A.L (11-20s)", "6-10 min", "8-10 min"
  elif d <= 350:
    return "C.A.L (21-50s)", "5-7 min", "8-10 min"
  elif d <= 500:
    return "P.A.E (1-2 min)", "3-4 min", "8-10 min"
  else:
    return "C.A.E (>2 min)", "1.5-2.5 min", "8-10 min"


# ==========================================
# 1. PERFIL Y CALCULADORA DE RITMOS
# ==========================================
if menu == "📊 Perfil y Calculadora de Ritmos":
  st.header("Perfil de Entrenamiento Personalizado por Atleta")
  if df_atletas.empty:
    st.warning("No hay atletas registrados.")
  else:
    col1, col2 = st.columns([1, 2])
    with col1:
      atleta_seleccionado = st.selectbox(
          "Seleccione al Atleta", df_atletas["Nombre del Atleta"].unique()
      )
      datos_atleta = df_atletas[
          df_atletas["Nombre del Atleta"] == atleta_seleccionado
      ].iloc[0]
      st.markdown("---")
      st.subheader("📋 Datos Base")
      st.write(f"**Categoría:** {datos_atleta['Categoría']}")
      st.write(f"**Especialidad:** {datos_atleta['Especialidad']}")
      st.write(f"**Prueba Base:** {datos_atleta['Prueba Base']}")
      st.write(
          f"**Marca Objetivo:** {datos_atleta['Marca Objetivo (s)']} segundos"
      )
      st.markdown("---")
      intensidad = st.slider(
          "Porcentaje de Intensidad (%)", 70, 110, 100, 5
      )
    with col2:
      st.subheader(
          f"Tabla de Ritmos y Pausas ({intensidad}% de la Marca Objetivo)"
      )
      base_dist_str = str(datos_atleta["Prueba Base"]).lower()
      base_dist = (
          float(base_dist_str.replace("km", "")) * 1000
          if "km" in base_dist_str
          else float(base_dist_str.replace("m", ""))
      )
      base_marca = float(datos_atleta["Marca Objetivo (s)"])
      v_media = base_dist / base_marca
      v_ajustada = v_media * (intensidad / 100.0)

      # Generar modelo biomecánico por tramos
      distancias = [
          10,
          20,
          30,
          40,
          50,
          60,
          70,
          80,
          90,
          100,
          150,
          200,
          250,
          300,
          350,
          400,
          450,
          500,
          600,
          700,
          800,
          900,
          1000,
          1200,
          1500,
          2000,
          3000,
          5000,
      ]
      tabla_resultados = []
      for d in distancias:
        if d <= base_dist * 2.5:
          # Aplicar factor de aceleración inicial y fatiga acumulada
          if d <= 30:
            factor_acel = 1.25 - (d / 120.0)
            t = (d / v_ajustada) * factor_acel
          elif d <= 100:
            t = (d / v_ajustada) * 1.03
          else:
            factor_fatiga = 1.0 + (d / 1500.0)
            t = (d / v_ajustada) * factor_fatiga

          if d == base_dist:
            t = base_marca * (100 / intensidad)

          vel_tramo = d / t if t > 0 else 0
          sistema, pausa_micro, pausa_macro = obtener_sistema_pausa(d)
          tabla_resultados.append({
              "Distancia (m)": d,
              "Tiempo (s)": round(t, 2),
              "Vel. Media (m/s)": round(vel_tramo, 2),
              "Ritmo 100m (s)": round((t / d) * 100, 2) if d > 0 else 0,
              "Pausa Micro": pausa_micro,
              "Sistema Energético": sistema,
          })
      df_resultado = pd.DataFrame(tabla_resultados)
      st.dataframe(df_resultado, use_container_width=True, height=400)
      csv = df_resultado.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="📥 Descargar Plan de Entrenamiento (CSV)",
          data=csv,
          file_name=(
              f"ritmos_{atleta_seleccionado.replace(' ', '_')}_{intensidad}pct.csv"
          ),
          mime="text/csv",
      )

# ==========================================
# 2. CALCULADORA POR DISTANCIA Y TIEMPO OBJETIVO
# ==========================================
elif menu == "⚡ Calculadora por Distancia y Tiempo Objetivo":
  st.header("Calculadora Biomecánica de Ritmos por Tramos")
  st.markdown(
      "Modelo avanzado que contempla la **fase de aceleración pendular inicial"
      " (0-30m)** y la **tasa de fatiga/deceleración** en distancias"
      " prolongadas."
  )

  tipo_prueba = st.selectbox(
      "Selecciona la Prueba de Referencia del Atleta:",
      [
          "Atleta de 100m (Límite: 350m)",
          "Atleta de 200m (Límite: 500m)",
          "Atleta de 400m u 800m (Límite: 1,000m)",
      ],
  )

  if "100m" in tipo_prueba:
    max_limite = 350.0
    val_defecto = 100.0
    especialidad_tipo = "100m"
  elif "200m" in tipo_prueba:
    max_limite = 500.0
    val_defecto = 200.0
    especialidad_tipo = "200m"
  else:
    max_limite = 1000.0
    val_defecto = 400.0
    especialidad_tipo = "400m"

  col_in1, col_in2, col_in3 = st.columns(3)
  with col_in1:
    custom_dist = st.number_input(
        "Distancia Objetivo (metros)",
        min_value=10.0,
        max_value=max_limite,
        value=val_defecto,
        step=10.0,
    )
  with col_in2:
    custom_time = st.number_input(
        "Tiempo Objetivo (segundos)",
        min_value=1.0,
        max_value=3600.0,
        value=52.0,
        step=0.1,
    )
  with col_in3:
    custom_intensidad = st.slider(
        "Porcentaje de Intensidad (%)", 50, 120, 100, 5
    )

  # Velocidad base neta
  v_base = custom_dist / custom_time
  v_ajustada = v_base * (custom_intensidad / 100.0)

  st.markdown("---")
  st.subheader("📊 Resultados del Modelo Biomecánico")

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Velocidad Media Global", f"{v_ajustada:.2f} m/s")
  m2.metric("Tiempo Total Estimado", f"{custom_time * (100/custom_intensidad):.2f} s")
  m3.metric("Ritmo Base (s/100m)", f"{(custom_time/custom_dist)*100:.2f} s")
  sistema_auto, pausa_micro_auto, pausa_macro_auto = obtener_sistema_pausa(
      custom_dist
  )
  m4.metric("Sistema Energético", sistema_auto)

  st.info(
      f"**Estrategia de Recuperación (Pausas):** Microciclo: **{pausa_micro_auto}**"
      f" | Macrociclo: **{pausa_macro_auto}** (Garantiza resíntesis de PCr)."
  )

  st.subheader("Desglose de Parciales con Aceleración y Fatiga")

  if "100m" in tipo_prueba:
    pasos = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 250, 300, 350]
  elif "200m" in tipo_prueba:
    pasos = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        150,
        200,
        250,
        300,
        350,
        400,
        450,
        500,
    ]
  else:
    pasos = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        150,
        200,
        250,
        300,
        350,
        400,
        450,
        500,
        600,
        700,
        800,
        900,
        1000,
    ]

  desglose = []
  for p in pasos:
    if p <= custom_dist:
      # Modelado no lineal de parciales
      if p <= 30:
        factor_acel = 1.25 - (p / 120.0)
        t_p = (p / v_ajustada) * factor_acel
      elif p <= 100:
        t_p = (p / v_ajustada) * 1.03
      else:
        if especialidad_tipo == "100m":
          f_fatiga = 1.0 + (p / 2000.0)
        elif especialidad_tipo == "200m":
          f_fatiga = 1.0 + (p / 1600.0)
        else:
          f_fatiga = 1.0 + (p / 1100.0)
        t_p = (p / v_ajustada) * f_fatiga

      if p == custom_dist:
        t_p = custom_time

      vel_tramo = p / t_p if t_p > 0 else 0
      desglose.append({
          "Distancia Parcial (m)": p,
          "Tiempo Parcial (s)": round(t_p, 2),
          "Vel. Media Tramo (m/s)": round(vel_tramo, 2),
          "Ritmo (s/100m)": round((t_p / p) * 100, 2) if p > 0 else 0,
      })

  df_desglose = pd.DataFrame(desglose)
  st.dataframe(df_desglose, use_container_width=True)

# ==========================================
# 3. REGISTRAR NUEVO ATLETA
# ==========================================
elif menu == "➕ Registrar Nuevo Atleta":
  st.header("Registro de Nuevos Atletas")
  with st.form("form_nuevo_atleta"):
    col_a, col_b = st.columns(2)
    with col_a:
      nombre = st.text_input("Nombre del Atleta")
      categoria = st.selectbox(
          "Categoría", ["Sub-16", "Sub-18", "Sub-20", "Junior", "Senior", "Máster"]
      )
      especialidad = st.selectbox(
          "Especialidad", ["Velocista", "Medio Fondo", "Fondo", "Vallas", "Saltos"]
      )
    with col_b:
      prueba_base = st.selectbox(
          "Prueba Base", ["60m", "100m", "200m", "400m", "800m", "1500m"]
      )
      marca_objetivo = st.number_input(
          "Marca Objetivo (en segundos)",
          min_value=5.0,
          max_value=600.0,
          value=12.0,
          step=0.1,
      )
    submit_button = st.form_submit_button(label="💾 Guardar Atleta")
    if submit_button:
      if nombre:
        dist_num = (
            float(prueba_base.replace("m", ""))
            if "m" in prueba_base
            else 100.0
        )
        vel_media = dist_num / marca_objetivo
        new_id = int(df_atletas["ID"].max() + 1) if not df_atletas.empty else 1
        nuevo_registro = pd.DataFrame([{
            "ID": new_id,
            "Nombre del Atleta": nombre,
            "Categoría": categoria,
            "Especialidad": especialidad,
            "Prueba Base": prueba_base,
            "Marca Objetivo (s)": marca_objetivo,
            "Velocidad Media (m/s)": round(vel_media, 6),
        }])
        df_actualizado = pd.concat(
            [df_atletas, nuevo_registro], ignore_index=True
        )
        try:
          with pd.ExcelWriter(
              file_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
          ) as writer:
            df_actualizado.to_excel(
                writer, sheet_name="Registro Atletas", index=False
            )
          st.success(
              f"¡Atleta '{nombre}' registrado con éxito en la base de datos!"
          )
          st.rerun()
        except Exception as e:
          st.error(f"Error al guardar en el archivo Excel: {e}")
      else:
        st.warning("Por favor, ingresa al menos el nombre del atleta.")
  st.subheader("Atletas Registrados Actualmente")
  st.dataframe(df_atletas, use_container_width=True)

# ==========================================
# 4. EDITAR O ELIMINAR ATLETAS
# ==========================================
elif menu == "✏️ Editar o Eliminar Atletas":
  st.header("Gestión y Edición de Atletas Registrados")
  if df_atletas.empty:
    st.info("No hay atletas en la base de datos para editar o eliminar.")
  else:
    atleta_a_gestionar = st.selectbox(
        "Selecciona el Atleta que deseas Modificar o Eliminar",
        df_atletas["Nombre del Atleta"].unique(),
    )
    atleta_row = df_atletas[
        df_atletas["Nombre del Atleta"] == atleta_a_gestionar
    ].iloc[0]

    col_ed1, col_ed2 = st.columns(2)
    with col_ed1:
      st.subheader("📝 Editar Datos del Atleta")
      with st.form("form_editar_atleta"):
        nuevo_nombre = st.text_input(
            "Nombre del Atleta", value=str(atleta_row["Nombre del Atleta"])
        )

        categorias_lista = [
            "Sub-16",
            "Sub-18",
            "Sub-20",
            "Junior",
            "Senior",
            "Máster",
        ]
        cat_idx = (
            categorias_lista.index(atleta_row["Categoría"])
            if atleta_row["Categoría"] in categorias_lista
            else 0
        )
        nueva_categoria = st.selectbox(
            "Categoría", categorias_lista, index=cat_idx
        )

        especialidades_lista = [
            "Velocista",
            "Medio Fondo",
            "Fondo",
            "Vallas",
            "Saltos",
        ]
        esp_idx = (
            especialidades_lista.index(atleta_row["Especialidad"])
            if atleta_row["Especialidad"] in especialidades_lista
            else 0
        )
        nueva_especialidad = st.selectbox(
            "Especialidad", especialidades_lista, index=esp_idx
        )

        pruebas_lista = ["60m", "100m", "200m", "400m", "800m", "1500m"]
        p_idx = (
            pruebas_lista.index(atleta_row["Prueba Base"])
            if atleta_row["Prueba Base"] in pruebas_lista
            else 1
        )
        nueva_prueba = st.selectbox("Prueba Base", pruebas_lista, index=p_idx)

        nueva_marca = st.number_input(
            "Marca Objetivo (s)",
            min_value=5.0,
            max_value=600.0,
            value=float(atleta_row["Marca Objetivo (s)"]),
            step=0.1,
        )

        btn_actualizar = st.form_submit_button(
            label="💾 Guardar Cambios / Actualizar"
        )

        if btn_actualizar:
          d_num = (
              float(nueva_prueba.replace("m", ""))
              if "m" in nueva_prueba
              else 100.0
          )
          nueva_vel = d_num / nueva_marca

          df_atletas.loc[
              df_atletas["Nombre del Atleta"] == atleta_a_gestionar,
              [
                  "Nombre del Atleta",
                  "Categoría",
                  "Especialidad",
                  "Prueba Base",
                  "Marca Objetivo (s)",
                  "Velocidad Media (m/s)",
              ],
          ] = [
              nuevo_nombre,
              nueva_categoria,
              nueva_especialidad,
              nueva_prueba,
              nueva_marca,
              round(nueva_vel, 6),
          ]

          try:
            with pd.ExcelWriter(
                file_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
            ) as writer:
              df_atletas.to_excel(
                  writer, sheet_name="Registro Atletas", index=False
                )
            st.success(f"¡Atleta '{nuevo_nombre}' actualizado correctamente!")
            st.rerun()
          except Exception as e:
            st.error(f"Error al actualizar la base de datos: {e}")

    with col_ed2:
      st.subheader("🗑️ Eliminar Atleta")
      st.warning(
          f"¿Deseas eliminar permanentemente a **{atleta_a_gestionar}** de la"
          " base de datos?"
      )
      if st.button(f"❌ Borrar a {atleta_a_gestionar}", type="primary"):
        df_atletas_filtrado = df_atletas[
            df_atletas["Nombre del Atleta"] != atleta_a_gestionar
        ]
        try:
          with pd.ExcelWriter(
              file_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
          ) as writer:
            df_atletas_filtrado.to_excel(
                writer, sheet_name="Registro Atletas", index=False
            )
          st.success(
              f"Atleta '{atleta_a_gestionar}' eliminado con éxito de la base de"
              " datos."
          )
          st.rerun()
        except Exception as e:
          st.error(f"Error al eliminar al atleta: {e}")

    st.markdown("---")
    st.subheader("Base de Datos Actualizada de Atletas")
    st.dataframe(df_atletas, use_container_width=True)

# ==========================================
# 5. COMPARATIVA DE ATLETAS
# ==========================================
elif menu == "📈 Comparativa de Atletas":
  st.header("Módulo Gráfico Comparativo")
  if df_atletas.empty:
    st.info("No hay suficientes datos para mostrar gráficos.")
  else:
    df_chart = df_atletas.set_index("Nombre del Atleta")[
        "Velocidad Media (m/s)"
    ]
    st.bar_chart(df_chart)
