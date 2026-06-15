import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# CONFIGURACION
# ==========================================pyn

ARCHIVO = "usu_individual_T425.txt"

# CAMBIAR POR LOS AGLOMERADOS DEL TRABAJO
AGLOMERADOS = {
    4: "Gran Rosario",
    29: "Gran Tucumán"
}

# ==========================================
# CARGA DE DATOS
# ==========================================

print("Leyendo archivo...")

df = pd.read_csv(
    ARCHIVO,
    sep=";",
    decimal=",",
    low_memory=False
)

total_registros = df

total_registros_len = len(df)


# ==========================================
# CONVERSIONES
# ==========================================

columnas_numericas = [
    "PONDERA",
    "ESTADO",
    "ANO4",
    "AGLOMERADO",
    "P47T",
    "CH04",
    "CH06",
    "NIVEL_ED"
]

for col in columnas_numericas:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ==========================================
# FILTRO AGLOMERADOS
# ==========================================

df = df[
    df["AGLOMERADO"].isin(
        AGLOMERADOS.keys()
    )
]

# ==========================================
# VALORES FALTANTES
# ==========================================

# print("\nVALORES FALTANTES")

# print(
#     df[
#         ["P47T", "CH04", "CH06",
#          "NIVEL_ED", "ESTADO"]
#     ].isna().sum()
# )

# ==========================================
# CALCULO DE TASAS
# ==========================================

resultados = []

for (anio, aglo), grupo in df.groupby(
    ["ANO4", "AGLOMERADO"]
):

    poblacion = grupo["PONDERA"].sum()

    ocupados = grupo[
        grupo["ESTADO"] == 1
    ]["PONDERA"].sum()

    desocupados = grupo[
        grupo["ESTADO"] == 2
    ]["PONDERA"].sum()

    activos = grupo[
        grupo["ESTADO"].isin([1, 2])
    ]["PONDERA"].sum()

    tasa_actividad = (
        activos / poblacion * 100
        if poblacion > 0
        else 0
    )

    tasa_empleo = (
        ocupados / poblacion * 100
        if poblacion > 0
        else 0
    )

    tasa_desocupacion = (
        desocupados / activos * 100
        if activos > 0
        else 0
    )

    resultados.append({
        "ANIO": anio,
        "AGLOMERADO": aglo,
        "TASA_ACTIVIDAD": round(
            tasa_actividad, 2
        ),
        "TASA_EMPLEO": round(
            tasa_empleo, 2
        ),
        "TASA_DESOCUPACION": round(
            tasa_desocupacion, 2
        )
    })

tasas = pd.DataFrame(resultados)

# print("\nTASAS")

# print(tasas.head())

# ==========================================
# ANALISIS INGRESOS
# ==========================================

ingresos = df[
    (df["P47T"].notna()) &
    (df["P47T"] > 0)
]

ingresos_anuales = (
    ingresos
    .groupby(
        ["ANO4", "AGLOMERADO"]
    )["P47T"]
    .agg([
        "mean",
        "median",
        "min",
        "max"
    ])
    .reset_index()
)

# print("\n========== INGRESOS ==========\n")

for _, fila in ingresos_anuales.iterrows():

    nombre = AGLOMERADOS.get(
        fila["AGLOMERADO"],
        str(fila["AGLOMERADO"])
    )

    print(f"""
Año: {int(fila['ANO4'])}
Aglomerado: {nombre}

Ingreso Promedio: ${fila['mean']:,.0f}
Ingreso Mediano: ${fila['median']:,.0f}

Ingreso Mínimo: ${fila['min']:,.0f}
Ingreso Máximo: ${fila['max']:,.0f}
""")

# ==========================================
# OUTLIERS
# ==========================================

Q1 = ingresos["P47T"].quantile(0.25)
Q3 = ingresos["P47T"].quantile(0.75)

IQR = Q3 - Q1

lim_inf = Q1 - 1.5 * IQR
lim_sup = Q3 + 1.5 * IQR

outliers = ingresos[
    (ingresos["P47T"] < lim_inf)
    |
    (ingresos["P47T"] > lim_sup)
]

# print("\n========== OUTLIERS ==========\n")

# print(
#     f"Se detectaron {len(outliers)} valores atípicos (outliers) en la variable de ingresos."
# )


# ==========================================
# INGRESO POR SEXO
# ==========================================

ingreso_sexo = (
    ingresos
    .groupby(
        ["ANO4", "AGLOMERADO", "CH04"]
    )["P47T"]
    .median()
    .reset_index()
)

# ==========================================
# INGRESO POR NIVEL EDUCATIVO
# ==========================================

ingreso_educacion = (
    ingresos
    .groupby(
        ["ANO4", "AGLOMERADO", "NIVEL_ED"]
    )["P47T"]
    .median()
    .reset_index()
)

# ==========================================
# GRAFICO TASA EMPLEO
# ==========================================

plt.figure(figsize=(12, 6))

for aglo in tasas["AGLOMERADO"].unique():

    datos = tasas[
        tasas["AGLOMERADO"] == aglo
    ]

    plt.plot(
        datos["ANIO"],
        datos["TASA_EMPLEO"],
        marker="o",
        label=AGLOMERADOS.get(
    aglo,
    str(aglo)
)
    )

plt.title(
    "Evolucion de la tasa de empleo"
)

plt.xlabel("Año")
plt.ylabel("%")

plt.grid(True)
plt.legend()

plt.savefig(
    "grafico_empleo.png"
)

plt.close()

# ==========================================
# GRAFICO DESOCUPACION
# ==========================================

plt.figure(figsize=(12, 6))

for aglo in tasas["AGLOMERADO"].unique():

    datos = tasas[
        tasas["AGLOMERADO"] == aglo
    ]

    plt.plot(
        datos["ANIO"],
        datos["TASA_DESOCUPACION"],
        marker="o",
        label=AGLOMERADOS.get(
    aglo,
    str(aglo)
)
    )

plt.title(
    "Evolucion de la tasa de desocupacion"
)

plt.xlabel("Año")
plt.ylabel("%")

plt.grid(True)
plt.legend()

plt.savefig(
    "grafico_desocupacion.png"
)

plt.close()

# ==========================================
# GRAFICO INGRESOS
# ==========================================

plt.figure(figsize=(12, 6))

for aglo in ingresos_anuales[
    "AGLOMERADO"
].unique():

    datos = ingresos_anuales[
        ingresos_anuales[
            "AGLOMERADO"
        ] == aglo
    ]

    plt.plot(
        datos["ANO4"],
        datos["median"],
        marker="o",
        label=AGLOMERADOS.get(
    aglo,
    str(aglo)
)
    )

plt.title(
    "Ingreso mediano"
)

plt.xlabel("Año")
plt.ylabel("Pesos")

plt.grid(True)
plt.legend()

plt.savefig(
    "grafico_ingresos.png"
)

plt.close()

# ==========================================
# BOXPLOT INGRESOS
# ==========================================

plt.figure(figsize=(12, 6))

sns.boxplot(
    data=ingresos,
    x="ANO4",
    y="P47T"
)

plt.title(
    "Distribucion de ingresos"
)

plt.savefig(
    "boxplot_ingresos.png"
)

plt.close()

# ==========================================
# EXPORTAR RESULTADOS
# ==========================================

with pd.ExcelWriter(
    "resultado_eph.xlsx"
) as writer:

    tasas.to_excel(
        writer,
        sheet_name="Tasas",
        index=False
    )

    ingresos_anuales.to_excel(
        writer,
        sheet_name="Ingresos",
        index=False
    )

    ingreso_sexo.to_excel(
        writer,
        sheet_name="Ingreso_Sexo",
        index=False
    )

    ingreso_educacion.to_excel(
        writer,
        sheet_name="Ingreso_Educacion",
        index=False
    )

    outliers.to_excel(
        writer,
        sheet_name="Outliers",
        index=False
    )

# ==========================================
# PUNTO 1 - ANALISIS UNIVARIADO
# ==========================================

print("\n========== PUNTO 1: ANALISIS UNIVARIADO ==========")



print(f"Registros leidos: {total_registros_len}")

print(
    f"Registros luego del filtro: {len(df)}"
)

for codigo, cantidad in df["AGLOMERADO"].value_counts().sort_index().items():

    nombre = AGLOMERADOS.get(
        codigo,
        str(codigo)
    )

    print(
        f"{nombre}: {cantidad} registros"
    )

print("\nVALORES FALTANTES")

descripciones = {
    "P47T": "Ingreso total individual",
    "CH04": "Sexo",
    "CH06": "Edad",
    "NIVEL_ED": "Nivel educativo",
    "ESTADO": "Condición de actividad"
}

faltantes = df[
    ["P47T", "CH04", "CH06", "NIVEL_ED", "ESTADO"]
].isna().sum()

for variable, cantidad in faltantes.items():
    print(
        f"{variable} - {descripciones[variable]}: "
        f"{cantidad} registros faltantes"
        f" ({cantidad / len(df) * 100:.2f}%)"
    )

print("\nVALORES ATIPICOS (OUTLIERS)")

cantidad_outliers = len(outliers)

print(f"Cantidad de outliers detectados: {cantidad_outliers}")

print(
    f"Representan el {(cantidad_outliers / len(ingresos) * 100):.2f}% "
    "de los registros con ingresos."
)

print(f"Ingreso mínimo de la muestra: ${ingresos['P47T'].min():,.0f}")
print(f"Ingreso máximo de la muestra: ${ingresos['P47T'].max():,.0f}")

print(f"Límite inferior utilizado: ${lim_inf:,.0f}")
print(f"Límite superior utilizado: ${lim_sup:,.0f}")

if cantidad_outliers > 0:

    print(
        f"Ingreso mínimo entre los outliers: "
        f"${outliers['P47T'].min():,.0f}"
    )

    print(
        f"Ingreso máximo entre los outliers: "
        f"${outliers['P47T'].max():,.0f}"
    )

print(
    "\nInterpretación:"
)

print(
    "Los valores atípicos corresponden a ingresos "
    "que se encuentran fuera de los límites definidos "
    "por el método del rango intercuartílico (IQR)."
)

print(
    "Estos casos pueden influir significativamente "
    "en el ingreso promedio, por lo que la mediana "
    "resulta una medida más robusta para describir "
    "la distribución de ingresos."
)


print("\nRESUMEN ESTADISTICO DE INGRESOS")

desc = ingresos["P47T"].describe()

print(f"Cantidad de registros: {int(desc['count'])}")
print(f"Ingreso promedio: ${desc['mean']:,.0f}")
print(f"Ingreso minimo: ${desc['min']:,.0f}")
print(f"Percentil 25: ${desc['25%']:,.0f}")
print(f"Mediana: ${desc['50%']:,.0f}")
print(f"Percentil 75: ${desc['75%']:,.0f}")
print(f"Ingreso maximo: ${desc['max']:,.0f}")
print(f"Desvio estandar: ${desc['std']:,.0f}")

# ==========================================
# PUNTO 2 - ANALISIS MULTIVARIADO
# ==========================================

print("\n========== PUNTO 2: ANALISIS MULTIVARIADO ==========")

print("\nTasas")
print(tasas)

# print("\nIngreso mediano por sexo")
# print(ingreso_sexo)

print("\nINGRESO MEDIANO POR SEXO Y AGLOMERADO")

for _, fila in ingreso_sexo.iterrows():

    aglomerado = AGLOMERADOS.get(
        fila["AGLOMERADO"],
        str(fila["AGLOMERADO"])
    )

    sexo = (
        "Varon"
        if fila["CH04"] == 1
        else "Mujer"
    )

    print(
        f"{aglomerado} - {sexo}: "
        f"${fila['P47T']:,.0f}"
    )

# print("\nIngreso mediano por nivel educativo")
# print(ingreso_educacion)
print("\nINGRESO MEDIANO POR NIVEL EDUCATIVO Y AGLOMERADO")

for _, fila in ingreso_educacion.iterrows():

    aglomerado = AGLOMERADOS.get(
        fila["AGLOMERADO"],
        str(fila["AGLOMERADO"])
    )

    print(
        f"{aglomerado} - "
        f"Nivel {int(fila['NIVEL_ED'])}: "
        f"${fila['P47T']:,.0f}"
    )

# ==========================================
# PUNTO 3 - VISUALIZACION
# ==========================================

print("\n========== PUNTO 3: VISUALIZACION ==========")

print("Graficos generados:")
print("- grafico_empleo.png")
print("- grafico_desocupacion.png")
print("- grafico_ingresos.png")
print("- boxplot_ingresos.png")

# ==========================================
# PUNTO 4 - IMPUTACION
# ==========================================

print("\n========== PUNTO 4: IMPUTACION ==========")
print("No implementado en esta version.")

print("\nProceso finalizado.")
print("Archivo generado: resultado_eph.xlsx")