import pandas as pd
import matplotlib.pyplot as plt


def graficar_datos_acumulados():
    try:
        df_fitness = pd.read_csv("Map2_Eucli_50Gen/datos_fitness5.csv")
        if df_fitness.empty:
            print("No hay datos de fitness para graficar.")
            return
    except FileNotFoundError:
        print("El archivo 'datos_fitness3.csv' no existe.")
        return

    # Continuar con la generación de gráficos si hay datos
    df_grouped = df_fitness.groupby("Generacion").agg(
        {"Mejor Fitness": ["mean", "max"], "Fitness Promedio": "mean"}
    )

    plt.figure(figsize=(10, 5))
    plt.plot(
        df_grouped.index,
        df_grouped["Mejor Fitness"]["mean"],
        label="Mejor Fitness",
        linewidth=3.5,
        linestyle="-",
    )
    plt.plot(
        df_grouped.index,
        df_grouped["Fitness Promedio"]["mean"],
        label="Fitness Promedio",
        linewidth=3.5,
        linestyle="--",
    )

    #plt.title("Mejor Fitness con Distancia Manhattan y refuerzo forzado durante el entrenamiento 2 con 20 generaciones")
    plt.xlabel("Generación", fontsize=30, fontname="Times New Roman")
    plt.ylabel("Fitness", fontsize=30, fontname="Times New Roman")
    plt.xticks(fontsize=30, fontname="Times New Roman")
    plt.yticks(fontsize=30, fontname="Times New Roman")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fontsize=20)
    plt.grid(True, linestyle="--", alpha=1)
    plt.show()

graficar_datos_acumulados()
