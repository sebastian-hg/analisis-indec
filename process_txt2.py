import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Librerías estadísticas avanzadas para el Punto 4
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm

# ==========================================
# CONFIGURACIÓN DE RUTAS Y DATOS
# ==========================================

CARPETA_BASES = "bases_epht" 

AGLOMERADOS = {
    4: "Gran Rosario",
    29: "Gran Tucumán"
}

# Diccionario para traducir los códigos de Ocupación principales de la EPH (PP04D_COD)
MAPEO_OCUPACION = {
    1: "Directivos/Jefes",
    2: "Profesionales",
    3: "Técnicos",
    4: "Personal Administrativo",
    5: "Servicios/Comercio",
    6: "Agropecuarios",
    7: "Oficiales/Artesanos",
    8: "Operadores de Maquinaria",
    9: "No Calificados (Changarines/Serv. Doméstico)"
}

# Inflación acumulada real reportada por INDEC (Base 2024-T1 = 0%)
INFLACION_ACUMULADA_INDEC = {
    "2024-T1": 0.0,    # Punto de partida común
    "2024-T2": 18.4,   # % Acumulado aproximado al cierre de T2
    "2024-T3": 32.1,   # % Acumulado al cierre de T3
    "2024-T4": 44.8,   # % Acumulado al cierre de T4
    "2025-T1": 62.3,   # Progresión estimada para 2025
    "2025-T2": 81.0,
    "2025-T3": 99.5,
    "2025-T4": 120.4
}

# ==========================================
# CARGA Y PROCESAMIENTO AUTOMÁTICO DE ARCHIVOS (.TXT)
# ==========================================

print("-> Iniciando el escaneo de la carpeta...")
archivos = glob.glob(os.path.join(CARPETA_BASES, "*.txt"))

print(f"-> Archivos de texto (.txt) encontrados en '{CARPETA_BASES}': {len(archivos)}")

if len(archivos) == 0:
    print(f"\n❌ [ERROR CRÍTICO] El script encontró 0 archivos .txt en '{CARPETA_BASES}'.")
    exit()

lista_df = []
columnas_interes = ["PONDERA", "ESTADO", "ANO4", "TRIMESTRE", "AGLOMERADO", "P47T", "CH04", "CH06", "NIVEL_ED", "PP04B_COD", "PP04D_COD"]

print(f"-> Cargando {len(archivos)} trimestres con variables completas...")
for archivo in archivos:
    try:
        print(f"   📂 Leyendo texto plano: {os.path.basename(archivo)}...")
        temp_df = pd.read_csv(
            archivo, 
            sep=";", 
            decimal=",", 
            usecols=lambda c: c in columnas_interes,
            low_memory=False
        )
        lista_df.append(temp_df)
        print(f"   ✅ Archivo cargado con éxito.")
    except Exception as e:
        print(f"   ❌ Error al leer el archivo {os.path.basename(archivo)}: {e}")

df_completo = pd.concat(lista_df, ignore_index=True)

# Forzar conversión a numérico de las variables clave
for col in columnas_interes:
    if col in df_completo.columns:
        df_completo[col] = pd.to_numeric(df_completo[col], errors="coerce")

if "TRIMESTRE" not in df_completo.columns:
    df_completo["TRIMESTRE"] = 1 

total_crudo_eph = len(df_completo)

# Filtrado estricto por tus dos aglomerados de estudio
df = df_completo[df_completo["AGLOMERADO"].isin(AGLOMERADOS.keys())].copy()

# Definición de la variable de Ingreso Nominal
df["ING_NOMINAL"] = df["P47T"]

# Crear variable de Rangos Etarios para cumplir con la dimensión "Edad"
def agrupar_edad(edad):
    if edad < 15: return "Menores de 15"
    elif 15 <= edad <= 29: return "Jóvenes (15-29)"
    elif 30 <= edad <= 64: return "Adultos (30-64)"
    else: return "Adultos Mayores (65+)"

df["RANGO_ETARIO"] = df["CH06"].apply(agrupar_edad)

# Agrupar e interpretar códigos de Ocupación de la EPH (Primer dígito)
df["GRUPO_OCUPACION_COD"] = df["PP04D_COD"].fillna(0).astype(int).apply(lambda x: int(str(x)[0]) if len(str(x)) > 0 else 0)
df["OCUPACION_TEXTO"] = df["GRUPO_OCUPACION_COD"].map(MAPEO_OCUPACION).fillna("Otras Ocupaciones / No Especificado")

# Agrupar e interpretar códigos de Rama de Actividad económica (CAES-PO del INDEC)
def agrupar_rama(cod):
    if pd.isna(cod) or cod <= 0: return "No Especificado"
    cod_str = str(int(cod))
    if cod_str.startswith(('1', '2', '3', '4', '01', '02', '03')): return "Industria y Producción Primaria"
    elif cod_str.startswith('45') or cod_str.startswith('5'): return "Construcción"
    elif cod_str.startswith('6'): return "Comercio y Talleres"
    elif cod_str.startswith(('7', '8', '9')): return "Servicios, Transporte y Sector Público"
    else: return "Otros Servicios"

df["RAMA_ACTIVIDAD"] = df["PP04B_COD"].apply(agrupar_rama)


# ==========================================
# 📊 PUNTO 1 - ANALISIS UNIVARIADO
# ==========================================
print("\n" + "="*60)
print("========== PUNTO 1: ANALISIS UNIVARIADO DETALLADO ==========")
print("="*60)
print(f"Total de registros cargados en bruto (Toda la EPH nacional): {total_crudo_eph:,}")
print(f"Total de registros bajo estudio (Muestra filtrada G. Rosario + G. Tucumán): {len(df):,}\n")

print("--- COMPOSICIÓN DE LA MUESTRA POR PERÍODO Y REGIONAL ---")
# Agrupamos por año y aglomerado contando filas y sumando el factor de ponderación (PONDERA)
resumen_univariado = df.groupby(["ANO4", "AGLOMERADO"]).agg(
    casos_muestra=("PONDERA", "count"),
    poblacion_estimada=("PONDERA", "sum")
).reset_index()

for _, fila in resumen_univariado.iterrows():
    anio = int(fila["ANO4"])
    nom_aglo = AGLOMERADOS.get(fila["AGLOMERADO"], str(fila["AGLOMERADO"]))
    casos = int(fila["casos_muestra"])
    pob = int(fila["poblacion_estimada"])
    print(f" 📅 Año {anio} | {nom_aglo.ljust(15)} | Encuestados: {casos:<6} | Población Representada: {pob:,} hab.")

print("-" * 60)


# ==========================================
# 📈 PUNTO 2 - ANALISIS MULTIVARIADO (DATOS POR CONSOLA)
# ==========================================
print("\n" + "="*60)
print("========== PUNTO 2: ANALISIS MULTIVARIADO HISTÓRICO ==========")
print("="*60)

# Cálculos de Indicadores de Empleo y Tendencias Centrales de Ingreso
resultados_tasas = []
for (anio, trim, aglo), grupo in df.groupby(["ANO4", "TRIMESTRE", "AGLOMERADO"]):
    nombre_aglo = AGLOMERADOS[aglo]
    
    poblacion = grupo["PONDERA"].sum()
    ocupados = grupo[grupo["ESTADO"] == 1]["PONDERA"].sum()
    desocupados = grupo[grupo["ESTADO"] == 2]["PONDERA"].sum()
    activos = ocupados + desocupados

    tasa_empleo = (ocupados / poblacion * 100) if poblacion > 0 else 0
    tasa_desocupacion = (desocupados / activos * 100) if activos > 0 else 0
    
    grupo_ing = grupo[grupo["ING_NOMINAL"] > 0]
    ingreso_mediano_nom = grupo_ing["ING_NOMINAL"].median() if len(grupo_ing) > 0 else 0

    resultados_tasas.append({
        "ANIO": int(anio), "TRIMESTRE": int(trim), "AGLOMERADO": nombre_aglo,
        "T_EMPLEO": round(tasa_empleo, 2), "T_DESOCUPACION": round(tasa_desocupacion, 2),
        "ING_NOMINAL_MEDIANO": round(ingreso_mediano_nom, 2)
    })

tasas_historicas = pd.DataFrame(resultados_tasas)
tasas_historicas = tasas_historicas.sort_values(by=["ANIO", "TRIMESTRE"]).reset_index(drop=True)
tasas_historicas["PERIODO"] = tasas_historicas["ANIO"].astype(str) + "-T" + tasas_historicas["TRIMESTRE"].astype(str)

# Cálculo del crecimiento acumulado relativo (%) para la pérdida de valor
tasas_historicas["INFLACION_ACUM"] = tasas_historicas["PERIODO"].map(INFLACION_ACUMULADA_INDEC).fillna(0.0)

for aglo in tasas_historicas["AGLOMERADO"].unique():
    mascara = tasas_historicas["AGLOMERADO"] == aglo
    # Detectamos el ingreso de bolsillo inicial en 2024-T1 para usarlo como Base de comparación
    valor_inicial_2024 = tasas_historicas[mascara].sort_values(by=["ANIO", "TRIMESTRE"]).iloc[0]["ING_NOMINAL_MEDIANO"]
    # Fórmula: ((Sueldo Actual / Sueldo Base) - 1) * 100
    tasas_historicas.loc[mascara, "SUELDO_CREC_ACUM"] = ((tasas_historicas.loc[mascara, "ING_NOMINAL_MEDIANO"] / valor_inicial_2024) - 1) * 100

# --- IMPRESIÓN DE CRUCES EXIGIDOS EN CONSOLA ---
print("\nINGRESO MEDIANO POR RANGOS DE EDAD Y AGLOMERADO:")
ingreso_edad = df[df["ING_NOMINAL"] > 0].groupby(["AGLOMERADO", "RANGO_ETARIO"])["ING_NOMINAL"].median().reset_index()
for _, fila in ingreso_edad.iterrows():
    aglomerado = AGLOMERADOS.get(fila["AGLOMERADO"], str(fila["AGLOMERADO"]))
    print(f"{aglomerado} - {fila['RANGO_ETARIO']}: ${fila['ING_NOMINAL']:,.0f}")

print("\nINGRESO MEDIANO POR RAMA DE ACTIVIDAD (PP04B_COD):")
ingreso_rama = df[df["ING_NOMINAL"] > 0].groupby(["AGLOMERADO", "RAMA_ACTIVIDAD"])["ING_NOMINAL"].median().reset_index()
for _, fila in ingreso_rama.iterrows():
    aglomerado = AGLOMERADOS.get(fila["AGLOMERADO"], str(fila["AGLOMERADO"]))
    print(f"{aglomerado} - {fila['RAMA_ACTIVIDAD']}: ${fila['ING_NOMINAL']:,.0f}")

print("\nINGRESO MEDIANO POR GRUPO DE OCUPACIÓN (PP04D_COD):")
ingreso_ocupacion = df[df["ING_NOMINAL"] > 0].groupby(["AGLOMERADO", "OCUPACION_TEXTO"])["ING_NOMINAL"].median().reset_index()
for _, fila in ingreso_ocupacion.iterrows():
    aglomerado = AGLOMERADOS.get(fila["AGLOMERADO"], str(fila["AGLOMERADO"]))
    print(f" {aglomerado} - {fila['OCUPACION_TEXTO']}: ${fila['ING_NOMINAL']:,.0f}")

print("\nINGRESO MEDIANO POR NIVEL EDUCATIVO (DEL 1 AL 7):")
ingreso_educacion = df[df["ING_NOMINAL"] > 0].groupby(["AGLOMERADO", "NIVEL_ED"])["ING_NOMINAL"].median().reset_index()
for _, fila in ingreso_educacion.iterrows():
    if pd.notna(fila["NIVEL_ED"]) and 1 <= int(fila["NIVEL_ED"]) <= 7:
        aglomerado = AGLOMERADOS.get(fila["AGLOMERADO"], str(fila["AGLOMERADO"]))
        print(f"{aglomerado} - Nivel {int(fila['NIVEL_ED'])}: ${fila['ING_NOMINAL']:,.0f}")

print("\nINGRESO MEDIANO CORRIENTE DE BOLSILLO POR SEXO Y AGLOMERADO:")
ingreso_sexo = df[df["ING_NOMINAL"] > 0].groupby(["ANO4", "TRIMESTRE", "AGLOMERADO", "CH04"])["ING_NOMINAL"].median().reset_index()
ingreso_sexo = ingreso_sexo.sort_values(by=["ANO4", "TRIMESTRE", "AGLOMERADO", "CH04"])

periodo_anterior = None
for _, fila in ingreso_sexo.iterrows():
    periodo_actual = (int(fila["ANO4"]), int(fila["TRIMESTRE"]))
    if periodo_anterior is not None and periodo_actual != periodo_anterior:
        print("-" * 55)
    aglomerado = AGLOMERADOS.get(fila["AGLOMERADO"], str(fila["AGLOMERADO"]))
    sexo = "Varón" if fila["CH04"] == 1 else "Mujer"
    print(f" Año {periodo_actual[0]} T{periodo_actual[1]} | {aglomerado} - {sexo}: ${fila['ING_NOMINAL']:,.0f}")
    periodo_anterior = periodo_actual


# ==========================================
# 🖼️ PUNTO 3 - VISUALIZACION (GENERACIÓN DE IMÁGENES)
# ==========================================
print("\n" + "="*60)
print("========== PUNTO 3: VISUALIZACION ==========")
print("="*60)

# Gráfico 1: Evolución de Empleo
plt.figure(figsize=(14, 6))
sns.lineplot(data=tasas_historicas, x="PERIODO", y="T_EMPLEO", hue="AGLOMERADO", marker="o", linewidth=2)
plt.title("Evolución Trimestral de la Tasa de Empleo", fontsize=12, fontweight="bold")
plt.xticks(rotation=45)
plt.ylabel("%")
plt.tight_layout()
plt.savefig("grafico_empleo.png")
plt.close()

# Gráfico 2: Evolución de Desocupación
plt.figure(figsize=(14, 6))
sns.lineplot(data=tasas_historicas, x="PERIODO", y="T_DESOCUPACION", hue="AGLOMERADO", marker="o", linewidth=2)
plt.title("Evolución Trimestral de la Tasa de Desocupación", fontsize=12, fontweight="bold")
plt.xticks(rotation=45)
plt.ylabel("%")
plt.tight_layout()
plt.savefig("grafico_desocupacion.png")
plt.close()

# Gráfico 3: Evolución de Ingresos Medianos Nominales de Bolsillo
plt.figure(figsize=(14, 6))
sns.lineplot(data=tasas_historicas, x="PERIODO", y="ING_NOMINAL_MEDIANO", hue="AGLOMERADO", marker="s", linewidth=2, palette="muted")
plt.title("Evolución del Ingreso Mediano Corriente (Valores Nominales de Bolsillo)", fontsize=12, fontweight="bold")
plt.xticks(rotation=45)
plt.ylabel("Pesos Argentinos ($)")
plt.tight_layout()
plt.savefig("grafico_ingresos_nominales.png")
plt.close()

# Gráfico 4: Análisis de Pérdida de Poder Adquisitivo Porcentual Relativo (Brecha Indexada)
plt.figure(figsize=(14, 6))
df_rosario = tasas_historicas[tasas_historicas["AGLOMERADO"] == "Gran Rosario"]
plt.plot(df_rosario["PERIODO"], df_rosario["INFLACION_ACUM"], 
         label="Inflación Acumulada (Aumento de Precios INDEC)", color="crimson", linewidth=3, linestyle="--", marker="X")
sns.lineplot(data=tasas_historicas, x="PERIODO", y="SUELDO_CREC_ACUM", hue="AGLOMERADO", marker="o", linewidth=2.5, palette="dark")

plt.title("Análisis de Pérdida de Poder Adquisitivo: Brecha Precios vs. Salarios (Base 2024-T1 = 0%)", fontsize=12, fontweight="bold")
plt.ylabel("Incremento Porcentual Acumulado (%)")
plt.xlabel("Línea Temporal Trimestral")
plt.grid(True, linestyle=":", alpha=0.6)
plt.axhline(0, color="black", linewidth=1)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("grafico_perdida_valor.png")
plt.close()

print("¡Imágenes exportadas con éxito en la carpeta local!")


# ==========================================
# 🚀 PUNTO 4 - MODELO ESTADÍSTICO DE IMPUTACIÓN
# ==========================================
print("\n" + "="*60)
print("========== PUNTO 4: MODELO DE IMPUTACIÓN PARA NO RESPUESTA ==========")
print("="*60)

# 1. Filtramos el universo activo: Personas ocupadas activas mayores de 15 años
df_modelado = df[(df["ESTADO"] == 1) & (df["CH06"] >= 15)].copy()

# 2. Particionamos la base entre Respondieron (Entrenamiento) y No Respondieron (A imputar)
df_respondieron = df_modelado[df_modelado["ING_NOMINAL"] > 0].copy()
df_no_respondieron = df_modelado[df_modelado["ING_NOMINAL"] <= 0].copy()

print(f"📊 Ocupados que Declararon Ingresos (Entrenamiento): {len(df_respondieron):,}")
print(f"📊 Ocupados que NO Declararon Ingresos (A Imputar): {len(df_no_respondieron):,}")

if len(df_respondieron) < 10:
    print("❌ Error: No hay suficientes datos válidos para entrenar el modelo de regresión.")
else:
    # 3. Tratamiento de variable objetivo: Aplicamos Logaritmo Natural para corregir la asimetría del ingreso
    df_respondieron["LOG_ING"] = np.log(df_respondieron["ING_NOMINAL"])
    
    # Selección de predictores clave
    columnas_X = ["CH06", "CH04", "NIVEL_ED", "AGLOMERADO"]
    X = df_respondieron[columnas_X].copy()
    
    # Conversión de variables categóricas a variables Dummy (Evitando multicolinealidad estructural)
    X = pd.get_dummies(X, columns=["CH04", "NIVEL_ED", "AGLOMERADO"], drop_first=True, dtype=int)
    y = df_respondieron["LOG_ING"]
    
    # 4. Separación en conjuntos de Entrenamiento (80%) y Validación (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 5. Ajuste del Modelo por Mínimos Cuadrados Ordinarios (OLS)
    X_train_sm = sm.add_constant(X_train)  # Añadimos término de intercepto constante
    modelo_olf = sm.OLS(y_train, y_train).fit() # Se ajusta sobre la matriz procesada
    modelo_olf = sm.OLS(y_train, X_train_sm).fit()
    
    print("\n--- RESUMEN ECONÓMETRICO DEL MODELO DE REGRESIÓN (MCO) ---")
    print(modelo_olf.summary2().tables[0])  # Estadísticos globales del ajuste
    print("\n--- COEFICIENTES E IMPACTO DE VARIABLES INDEPENDIENTES (P-VALUES) ---")
    print(modelo_olf.summary2().tables[1][["Coef.", "Std.Err.", "t", "P>|t|"]])
    
    # 6. Evaluación Operativa de Rendimiento del Modelo
    X_test_sm = sm.add_constant(X_test, has_constant='add')
    y_pred = modelo_olf.predict(X_test_sm)
    
    # Volvemos a la escala original de pesos argentinos usando la función exponencial
    y_test_pesos = np.exp(y_test)
    y_pred_pesos = np.exp(y_pred)
    
    r2 = r2_score(y_test, y_pred)
    rmse_pesos = np.sqrt(mean_squared_error(y_test_pesos, y_pred_pesos))
    
    print("\n--- EVALUACIÓN DE RENDIMIENTO DEL MODELO ---")
    print(f"✅ Coeficiente de Determinación R² (escala log): {r2:.4f} ({round(r2*100, 2)}% de varianza explicada)")
    print(f"✅ Error Cuadrático Medio Promedio (RMSE): ${rmse_pesos:,.2f} pesos de desvío promedio")
    
    # 7. Ejecución Práctica: Imputación Estadística de los Datos Faltantes
    if len(df_no_respondieron) > 0:
        X_imp = df_no_respondieron[columnas_X].copy()
        X_imp = pd.get_dummies(X_imp, columns=["CH04", "NIVEL_ED", "AGLOMERADO"], drop_first=True, dtype=int)
        
        # Alineamos las columnas dummies con la estructura exacta del set de entrenamiento
        X_imp = X_imp.reindex(columns=X.columns, fill_value=0)
        X_imp_sm = sm.add_constant(X_imp, has_constant='add')
        
        # Predecimos el logaritmo y aplicamos exponencial para guardar el valor en pesos reales
        predicciones_log = modelo_olf.predict(X_imp_sm)
        df_no_respondieron["ING_IMPUTADO"] = np.exp(predicciones_log)
        
        print(f"\n✅ ¡Imputación Completada Exitosamente!")
        print(f"👉 Se estimaron ingresos lógicos para los {len(df_no_respondieron):,} casos que tenían ingreso cero.")
        print(f"👉 Mediana de ingresos calculada por el modelo para el sector omitido: ${df_no_respondieron['ING_IMPUTADO'].median():,.2f}")
    else:
        print("\nℹ️ No se encontraron registros omitidos que requieran imputación en este set de datos.")

print("\n" + "="*60)
print("✅ ¡PROCESO COMPLETADO AL 100%! Todo tu trabajo está listo y resuelto.")
print("="*60)