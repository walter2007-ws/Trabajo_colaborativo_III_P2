# Trabajo_colaborativo_III_P2
# Sensor Data Recovery Toolkit: Reconstrucción de Lecturas Térmicas mediante Interpolación

Este proyecto consiste en el diseño e implementación de un sistema de software dedicado al análisis y restauración de datos provenientes de entornos IoT y sistemas de monitoreo industrial. Utilizando un archivo de origen de datos reales (`sensor_temperatura.csv`), el sistema simula la pérdida de paquetes de telemetría provocada por fallas de conectividad o ruidos en los canales de transmisión, implementando el método matemático de **Interpolación Polinomial de Lagrange** en el nodo receptor para reconstruir con precisión las lecturas de temperatura perdidas.

Desde la perspectiva de la **Ingeniería de Software**, el sistema integra una interfaz gráfica interactiva, procesa estructuras de datos bidimensionales extraídas de sensores físicos y evalúa rigurosamente el rendimiento temporal ($ms$) del algoritmo para auditar su viabilidad en sistemas de monitoreo crítico en tiempo real.

---

## Requisitos del Proyecto (Elicitación de Requerimientos)

Para asegurar un desarrollo robusto y alineado con las buenas prácticas de arquitectura, el sistema se diseñó bajo los siguientes **Requisitos Funcionales (RF)**:

* **RF-01 (Importación de Telemetría Real):** El sistema debe ser capaz de abrir, parsear y cargar archivos estructurados (`.csv`) que contengan lecturas de sensores distribuidas en dos columnas fundamentales: Tiempo y Temperatura.
* **RF-02 (Simulación de Fallas en Red IoT):** El software debe simular la pérdida intermitente de paquetes eliminando de forma aleatoria registros del dataset original, almacenando por separado los datos supervivientes y los puntos de vacío informático.
* **RF-03 (Motor de Reconstrucción Numérica):** El módulo de cómputo debe invocar iterativamente el algoritmo de Lagrange para estimar la temperatura exacta en los instantes de tiempo donde se interrumpió la señal del sensor.
* **RF-04 (Métricas de Latencia y Benchmarking):** El sistema debe incorporar un cronómetro de alta precisión que registre en milisegundos el tiempo empleado por el procesador para recuperar el dataset completo.
* **RF-05 (Auditoría de Viabilidad):** El software debe contrastar de manera automatizada el tiempo total de cómputo contra un umbral crítico de tolerancia (~20 ms) para emitir un dictamen sobre el rendimiento del sistema en la consola o interfaz.
* **RF-06 (Despliegue del Reporte Visual):** Se debe renderizar un panel gráfico bidimensional interactivo que contraste las curvas originales del sensor de temperatura, los puntos de datos que se recibieron con éxito y las lecturas recuperadas artificialmente.

---

## Arquitectura y Estructura del Software

El código fuente está estrictamente modularizado en componentes independientes para garantizar una alta cohesión y facilitar la futura escalabilidad del sistema (como la migración a Splines Cúbicos en entornos de alta densidad de datos):

* **Módulo de Entrada/Salida (I/O):** Gestiona la lectura y segmentación de las columnas del archivo `sensor_temperatura.csv`.
* **`simular_transmision_red`**: Modula la fase de alteración de datos, aislando los vectores de llegada de los vectores perdidos a través de un muestreo combinatorio aleatorio.
* **`coeficiente_de_Lagrange`**: Resuelve de forma nativa la ponderación matemática ($L_i$) de los nodos de tiempo vecinos sobre cada vacío del sensor mediante multiplicaciones acumuladas.
* **`interpolador_lagrange`**: Orquesta el cálculo polinomial definitivo combinando las temperaturas conocidas con sus respectivos coeficientes de peso.
* **`evaluar_rendimiento_sistema`**: Controla el flujo del cronómetro de alta precisión (`time.perf_counter`), procesa el llenado dinámico de los arreglos en memoria y emite el juicio analítico de latencia.
* **`graficar_resultados`**: Mapea y renderiza el comportamiento del sensor sobre el lienzo gráfico.

---

## Interpretación del Reporte Gráfico

Al finalizar el procesamiento, el sistema genera un lienzo visual interactivo diseñado para la evaluación de fallas térmicas:

* **Línea Segmentada o Continua:** Representa el comportamiento histórico ideal y real registrado por el sensor de temperatura.
* **Puntos Azules (`o`):** Indican las lecturas de telemetría que fueron transmitidas con éxito y capturadas por el servidor central.
* **Cruces Rojas (`x`):** Representan el éxito del *Toolkit de Recuperación*, demostrando geométricamente cómo el algoritmo estimó la temperatura exacta del sensor en los momentos de desconexión.

---

