import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="App de Control de Ritmos e Intensidades",
    page_icon="🏃‍♂️",
    layout="wide",
)

file_path = "Calculadora_Ritmos_Atletas_BD.xlsx"


# Función para cargar datos de atletas
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
    "Calculadora automática de ritmos, parciales, intensidades y sistemas"
    " energéticos."
)

# Menú de navegación lateral
menu = st.sidebar.selectbox(
    "Menú de Navegación",
    [
        "📊 Perfil y Calculadora de Ritmos",
        "⚡ Calculadora por Distancia y Tiempo Objetivo",
        "➕ Registrar Nuevo Atleta",
        "📈 Comparativa de Atletas",
    ],
)

# Función lógica para asignar pausas y sistemas energéticos
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
# SECCIÓN 1: PERFIL Y CALCULADORA DE RITMOS
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
      velocidad_base = base_dist / base_marca
      velocidad_ajustada = velocidad_base * (intensidad / 100.0)

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
          tiempo_obj = d / velocidad_ajustada
          t_10m = 10 / velocidad_ajustada
          t_50m = 50 / velocidad_ajustada
          t_100m = 100 / velocidad_ajustada
          sistema, pausa_micro, pausa_macro = obtener_sistema_pausa(d)

          tabla_resultados.append({
              "Distancia (m)": d,
              "Tiempo (s)": round(tiempo_obj, 2),
              "Vel. (m/s)": round(velocidad_ajustada, 2),
              "Parcial 10m": round(t_10m, 2),
              "Parcial 50m": round(t_50m, 2),
              "Parcial 100m": round(t_100m, 2),
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
# SECCIÓN 2: NUEVA CALCULADORA POR DISTANCIA Y TIEMPO OBJETIVO
# ==========================================
elif menu == "⚡ Calculadora por Distancia y Tiempo Objetivo":
  st.header("Calculadora Automática de Ritmo por Distancia y Tiempo Objetivo")
  st.markdown(
      "Ingresa una distancia específica y el tiempo objetivo deseado para"
      " calcular de inmediato la velocidad exacta, los parciales y el sistema"
      " energético."
  )

  col_in1, col_in2, col_in3 = st.columns(3)
  with col_in1:
    custom_dist = st.number_input(
        "Distancia Objetivo (metros)",
        min_value=10.0,
        max_value=10000.0,
        value=400.0,
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

  # Cálculo automático
  vel_ms = custom_dist / custom_time
  vel_ajustada = vel_ms * (custom_intensidad / 100.0)
  tiempo_ajustado = custom_dist / vel_ajustada

  st.markdown("---")
  st.subheader("📊 Resultados del Cálculo Automático")

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Velocidad Resultante", f"{vel_ajustada:.2f} m/s")
  m2.metric("Tiempo Total Ajustado", f"{tiempo_ajustado:.2f} s")
  m3.metric("Parcial cada 100m", f"{100 / vel_ajustada:.2f} s")
  sistema_auto, pausa_micro_auto, pausa_macro_auto = obtener_sistema_pausa(
      custom_dist
  )
  m4.metric("Sistema Energético", sistema_auto)

  st.info(
      f"**Recomendación de Pausas:** Pausa Microciclo: **{pausa_micro_auto}** |"
      f" Pausa Macrociclo: **{pausa_macro_auto}**"
  )

  # Generar tabla fraccionada automática para esta distancia objetivo
  st.subheader("Desglose de Parciales Fraccionados")
  pasos = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 250, 300, 400]
  desglose = []
  for p in pasos:
    if p <= custom_dist:
      t_p = p / vel_ajustada
      desglose.append({
          "Distancia Parcial (m)": p,
          "Tiempo de Paso (s)": round(t_p, 2),
          "Ritmo (s/100m)": round(100 / vel_ajustada, 2),
      })

  df_desglose = pd.DataFrame(desglose)
  st.dataframe(df_desglose, use_container_width=True)

# ==========================================
# SECCIÓN 3: REGISTRAR NUEVO ATLETA
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
# SECCIÓN 4: COMPARATIVA DE ATLETAS
# ==========================================
elif menu == "📈 Comparativa de Atletas":
  st.header("Módulo Gráfico Comparativo")
  if df_atletas.empty:
    st.info("No hay suficientes datos para mostrar gráficos.")
  else:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=df_atletas,
        x="Nombre del Atleta",
        y="Velocidad Media (m/s)",
        palette="Blues_d",
        ax=ax,
    )
    ax.set_title(
        "Velocidad Media Base (m/s) por Atleta", fontsize=14, fontweight="bold"
    )
    ax.set_ylabel("Velocidad Media (m/s)")
    ax.set_xlabel("Atleta")
    plt.xticks(rotation=15)
    st.pyplot(fig)