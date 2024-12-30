import os
import pandas as pd
import matplotlib.pyplot as plt


def graficar_fitness_multiples_simulaciones(
    directorio="./Euclidiana/Eucli_50Gen",
    prefix="fitness_individual",
    extension=".csv",
):
    # Obtener todos los archivos que coinciden con el prefijo y extensión
    archivos = [
        f
        for f in os.listdir(directorio)
        if f.startswith(prefix) and f.endswith(extension)
    ]
    if not archivos:
        print("No se encontraron archivos de fitness para graficar.")
        return
    plt.figure(figsize=(12, 8))
    linestyles = ["-", "--", "-.", ":"]
    for i, archivo in enumerate(archivos):
        ruta_archivo = os.path.join(directorio, archivo)
        try:
            df = pd.read_csv(ruta_archivo)
            if df.empty:
                print(f"El archivo {archivo} está vacío. Saltando.")
                continue
            # Calcular promedio y desviación estándar por generación
            df_grouped = (
                df.groupby("generacion")["fitness"].agg(["mean", "std"]).reset_index()
            )
            # Extraer número de simulación del nombre del archivo (asumiendo formato 'fitness_individual_X.csv')
            simulacion_num = archivo.replace(prefix, "").replace(extension, "")
            # Graficar el promedio
            plt.plot(
                df_grouped["generacion"],
                df_grouped["mean"],
                label=f"Entrenamiento {simulacion_num} - Promedio",
                linewidth=3.5,  # Aumentar el tamaño de la línea
                linestyle=linestyles[i % len(linestyles)],  # Cambiar el estilo de línea
            )
            # Graficar la desviación estándar como área sombreadas
            plt.fill_between(
                df_grouped["generacion"],
                df_grouped["mean"] - df_grouped["std"],
                df_grouped["mean"] + df_grouped["std"],
                alpha=0.3,
                label=f"Entrenamiento {simulacion_num} - Desviación Estándar",
            )
        except Exception as e:
            print(f"Error al procesar el archivo {archivo}: {e}")

    plt.title(
        "Fitness Promedios y Desciaciones con Distancia Euclidiana en 50 Generaciones",
        fontsize=20,
        fontname="Times New Roman",
    )
    plt.xlabel("Generación", fontsize=20, fontname="Times New Roman")
    plt.ylabel("Fitness", fontsize=20, fontname="Times New Roman")
    plt.xticks(fontsize=20, fontname="Times New Roman")
    plt.yticks(fontsize=20, fontname="Times New Roman")

    # Ubicar la leyenda debajo de la gráfica
    plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.4), ncol=2, fontsize=12)
    plt.grid(True, linestyle="--", alpha=1)
    # Ajustar el layout para que no se corte la leyenda
    plt.tight_layout()
    # Crear el directorio para las gráficas si no existe
    # ruta_guardado = os.path.join(directorio, "Graficas")
    # if not os.path.exists(ruta_guardado):
    #     os.makedirs(ruta_guardado)
    # Guardar la gráfica
    # ruta_grafica = os.path.join(
    #     ruta_guardado, "Fitness_Promedio_Multiples_Simulaciones.png"
    # )
    plt.show()
    # print(f"Gráfica guardada en: {ruta_grafica}")


# Ejecutar las funciones
graficar_fitness_multiples_simulaciones()
