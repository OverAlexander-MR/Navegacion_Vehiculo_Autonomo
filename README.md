# Navegacion_Vehiculo_Autonomo

Proyecto en desarrollo de Inteligencia Artificial que se enfoca en la creación de un sistema de navegación para vehículos autónomos. Este sistema utiliza NEAT para el aprendizaje automático y técnicas de procesamiento de datos para permitir que un vehículo se desplace en un mapa de 2D.

## Descripción

El proyecto **Navegacion_Vehiculo_Autonomo** tiene como objetivo desarrollar una solución integral para la navegación autónoma de vehículos. Mediante el uso de sensores y procesamiento en tiempo real, el sistema es capaz de detectar y evitar obstáculos. Las principales funcionalidades incluyen:

- **Detección de Obstáculos:** Utilización de sensores para identificar y localizar obstáculos en el entorno del vehículo.
- **Planificación de Rutas:** Algoritmos que calculan la ruta más eficiente desde el punto A hasta el punto B, para eso se hace uso de la distancia Euclidiana, Manhattan y Chebyshev.
- **Toma de Decisiones:** Redes neuronales que procesan la información de los sensores para tomar decisiones en tiempo real.
- **Integración de Sensores:** Combinación de datos de múltiples entradas para una percepción precisa del entorno.

## Requisitos

- Python 3.12.3
- pygame==2.6.1
- neat-python==0.92

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/usuario/Navegacion_Vehiculo_Autonomo.git
   ```
2. Navegar al directorio del proyecto:
   ```bash
   cd Navegacion_Vehiculo_Autonomo
   ```
3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
