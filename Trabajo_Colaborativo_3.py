import numpy as np
import random as random
import time as time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Variables globales
datos_externos_x = None
datos_externos_y = None
datos_externos_perdidos = None

# --- Funciones Matemáticas ---
def coeficiente_de_Lagrange(objetivo_x, i, lista_x):
    n = len(lista_x)
    producto = 1
    for j in range(n):
        if j != i:
            numerador = objetivo_x - lista_x[j]
            denominador = lista_x[i] - lista_x[j]
            producto *= (numerador / denominador)
    return producto

def interpolador_lagrange(objetivo_x, puntos_x, puntos_y):
    n = len(puntos_x)
    suma = 0
    for i in range(n):
        producto_L = coeficiente_de_Lagrange(objetivo_x, i, puntos_x)
        suma += puntos_y[i] * producto_L
    return suma

def simular_transmision_red(numero_total_paquetes):
    x = np.arange(numero_total_paquetes + 1)
    y = np.sin(x)
    rand = random.randint(1, max(1, numero_total_paquetes - 1))
    indices_aleatorios = np.array(random.sample(list(x), rand), dtype=int)
    x_perdidos = x[indices_aleatorios]
    x_llegada = np.delete(x, indices_aleatorios)
    y_llegada = np.delete(y, indices_aleatorios)
    return x_llegada, y_llegada, x_perdidos

def evaluar_rendimiento_sistema(lista_paquetes_perdidos, x_llegada, y_llegada):
    n = len(lista_paquetes_perdidos)
    reconstruccion = []
    tiempo_inicio = time.perf_counter()
    for i in range(n):
        # Usar solo los 6 puntos más cercanos para evitar explosión numérica
        distancias = np.abs(x_llegada - lista_paquetes_perdidos[i])
        idx_cercanos = np.argsort(distancias)[:6]
        px = x_llegada[idx_cercanos]
        py = y_llegada[idx_cercanos]
        reconstruccion.append(interpolador_lagrange(lista_paquetes_perdidos[i], px, py))
    tiempo_final = time.perf_counter()
    tiempo_total = (tiempo_final - tiempo_inicio) * 1000
    return reconstruccion, tiempo_total

# --- Cargar Archivo ---
def cargar_archivo():
    global datos_externos_x, datos_externos_y, datos_externos_perdidos
    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar archivo de datos",
        filetypes=[("Archivos de texto o CSV", "*.txt *.csv"), ("Todos los archivos", "*.*")]
    )
    if ruta_archivo:
        try:
            datos = np.genfromtxt(ruta_archivo, delimiter=',', filling_values=np.nan)
            x_todos = datos[:, 0]
            y_todos = datos[:, 1]

            mascara_validos = ~np.isnan(y_todos)

            datos_externos_x = x_todos[mascara_validos]
            datos_externos_y = y_todos[mascara_validos]
            datos_externos_perdidos = x_todos[~mascara_validos]

            n_vacios = int(np.sum(~mascara_validos))
            lbl_archivo.config(text=f"Archivo cargado: {ruta_archivo.split('/')[-1]}", foreground="blue")
            entry_paquetes.config(state="disabled")
            messagebox.showinfo("Éxito", f"Puntos válidos: {len(datos_externos_x)}\nFallas detectadas: {n_vacios}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{str(e)}")

def limpiar_datos_externos():
    global datos_externos_x, datos_externos_y, datos_externos_perdidos
    datos_externos_x = None
    datos_externos_y = None
    datos_externos_perdidos = None
    lbl_archivo.config(text="Ningún archivo cargado", foreground="gray")
    entry_paquetes.config(state="normal")

# --- Ejecución Principal ---
def ejecutar_simulacion():
    global datos_externos_x, datos_externos_y, datos_externos_perdidos

    if datos_externos_x is not None:
        x_llegada = datos_externos_x
        y_llegada = datos_externos_y
        x_perdidos = datos_externos_perdidos

        if x_perdidos is None or len(x_perdidos) == 0:
            messagebox.showwarning("Sin fallas", "El archivo no tiene filas vacías.")
            return
        if len(x_llegada) < 2:
            messagebox.showwarning("Pocos datos", "Se necesitan al menos 2 puntos válidos.")
            return

        x_completo = np.sort(np.concatenate([x_llegada, x_perdidos]))
        y_completo = []
        for xi in x_completo:
            distancias = np.abs(x_llegada - xi)
            idx_cercanos = np.argsort(distancias)[:6]
            y_completo.append(interpolador_lagrange(xi, x_llegada[idx_cercanos], y_llegada[idx_cercanos]))
        y_completo = np.array(y_completo)

    else:
        try:
            total_paquetes = int(entry_paquetes.get())
            if total_paquetes < 3:
                messagebox.showwarning("Atención", "Ingresa al menos 3 paquetes.")
                return
        except ValueError:
            messagebox.showerror("Error", "Debes ingresar un número entero válido.")
            return

        x_llegada, y_llegada, x_perdidos = simular_transmision_red(total_paquetes)
        x_completo = np.arange(total_paquetes + 1)
        y_completo = np.sin(x_completo)

    datos_recuperados, tiempo_total = evaluar_rendimiento_sistema(x_perdidos, x_llegada, y_llegada)

    lbl_llegados.config(text=f"Puntos válidos: {len(x_llegada)}")
    lbl_perdidos.config(text=f"Datos recuperados: {[round(float(v), 4) for v in datos_recuperados]}")
    lbl_tiempo.config(text=f"Tiempo de ejecución: {tiempo_total:.4f} ms")

    if tiempo_total < 20:
        lbl_status.config(text="Rendimiento: BUENO", foreground="green")
    else:
        lbl_status.config(text="Rendimiento: LENTO", foreground="red")

    ax.clear()
    idx_ordenado = np.argsort(x_completo)
    ax.plot(x_completo[idx_ordenado], y_completo[idx_ordenado], linestyle='--', color='gray', label='Señal Base')
    ax.scatter(x_llegada, y_llegada, marker='o', color='blue', s=40, label='Datos Recibidos')
    ax.scatter(x_perdidos, datos_recuperados, marker='x', color='red', s=60, label='Reconstruidos (Lagrange)')
    ax.set_title("Recuperación de Información")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Valor del Sensor")
    ax.legend()
    canvas.draw()

# --- Interfaz ---
ventana = tk.Tk()
ventana.title("Sistema de Recuperación de Datos - Lagrange")
ventana.geometry("950x580")
ventana.rowconfigure(0, weight=1)
ventana.columnconfigure(1, weight=1)

panel_control = ttk.Frame(ventana, padding="15")
panel_control.grid(row=0, column=0, sticky="nsew")

ttk.Label(panel_control, text="Cargar Datos Reales", font=("Arial", 12, "bold")).pack(pady=5)
btn_cargar = ttk.Button(panel_control, text="Subir Archivo (.csv / .txt)", command=cargar_archivo)
btn_cargar.pack(pady=5)

lbl_archivo = ttk.Label(panel_control, text="Ningún archivo cargado", font=("Arial", 9, "italic"), foreground="gray")
lbl_archivo.pack(pady=2)

btn_limpiar = ttk.Button(panel_control, text="Volver a Simulación Interna", command=limpiar_datos_externos)
btn_limpiar.pack(pady=5)

ttk.Separator(panel_control, orient="horizontal").pack(fill="x", pady=10)

ttk.Label(panel_control, text="Simulación Automática", font=("Arial", 12, "bold")).pack(pady=5)
ttk.Label(panel_control, text="Número de Paquetes (Seno):").pack(pady=2)
entry_paquetes = ttk.Entry(panel_control, width=15)
entry_paquetes.insert(0, "10")
entry_paquetes.pack(pady=5)

btn_simular = ttk.Button(panel_control, text="Procesar y Graficar", command=ejecutar_simulacion)
btn_simular.pack(pady=15)

ttk.Separator(panel_control, orient="horizontal").pack(fill="x", pady=10)

ttk.Label(panel_control, text="Métricas del Sistema", font=("Arial", 11, "bold")).pack(pady=5)
lbl_llegados = ttk.Label(panel_control, text="Paquetes exitosos: -", wraplength=250)
lbl_llegados.pack(anchor="w", pady=2)
lbl_perdidos = ttk.Label(panel_control, text="Paquetes perdidos: -", wraplength=250)
lbl_perdidos.pack(anchor="w", pady=2)
lbl_tiempo = ttk.Label(panel_control, text="Tiempo de ejecución: -")
lbl_tiempo.pack(anchor="w", pady=2)
lbl_status = ttk.Label(panel_control, text="Rendimiento: -", font=("Arial", 10, "bold"))
lbl_status.pack(anchor="w", pady=10)

panel_grafica = ttk.Frame(ventana, padding="10")
panel_grafica.grid(row=0, column=1, sticky="nsew")

fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=panel_grafica)
canvas.get_tk_widget().pack(fill="both", expand=True)

ventana.mainloop()