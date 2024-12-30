import pandas as pd
import matplotlib.pyplot as plt


def graficar_datos_acumulados():
    try:
        # Leer los datos de fitness que necesita
        df_fitness = pd.read_csv("./Euclidiana/Eucli_50Gen/datos_fitness4.csv")
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

    # Cambiar el titulo segun sea el caso
    plt.title(
        "Mejor Fitness con Distancia Euclidiana y Refuerzo Forzado durante el entrenamiento 4 con 50 generaciones",
        fontsize=20,
        fontname="Times New Roman",
    )
    plt.xlabel("Generación", fontsize=20, fontname="Times New Roman")
    plt.ylabel("Fitness", fontsize=20, fontname="Times New Roman")
    plt.xticks(fontsize=20, fontname="Times New Roman")
    plt.yticks(fontsize=20, fontname="Times New Roman")
    plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.3), ncol=2, fontsize=20)
    plt.grid(True, linestyle="--", alpha=1)
    plt.tight_layout()
    plt.show()


graficar_datos_acumulados()
