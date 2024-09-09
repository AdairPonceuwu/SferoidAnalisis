import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

def simulacion():
    
    global current_index
    current_index = 0  # Inicializar la variable global current_index

    #####
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Simulacion crecimiento de 24 a 168 hrs")

    # Crear la figura y el eje 3D
    fig = plt.Figure()
    ax = fig.add_subplot(111, projection='3d')

    # Definir los parámetros para las 7 esferas
    params = [
        {'t': 24, 'c': 620.47, 'a': 597.00},
        {'t': 48, 'c': 627.56 , 'a': 593.19},
        {'t': 72, 'c': 672.44 , 'a': 612.85},
        {'t': 96, 'c': 757.51 , 'a': 722.11},
        {'t': 120, 'c': 796.05 , 'a': 792.48 },
        {'t': 144, 'c': 834.88 , 'a': 815.81 },
        {'t': 168, 'c': 957.14 , 'a': 852.44 }
    ]

    # Crear una esfera que representa la célula del asteroide
    np.random.seed(365)
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))

    # Índice de la esfera actual
    current_index = 0

    # Crear una etiqueta con instrucciones
    instructions = tk.Label(root, text="")
    instructions.pack(side=tk.BOTTOM, fill=tk.X)
    number_label = tk.Label(root, text="")
    number_label.pack(side=tk.BOTTOM, fill=tk.X)

    # Función para inicializar las minicélulas
    def initialize_cells(num_cells):
        np.random.seed(365)  # Establece la semilla para reproducibilidad
        cell_colors = np.array(['black'] * (num_cells // 3) + ['orange'] * (num_cells // 3) + ['blue'] * (num_cells - 2 * (num_cells // 3)))
        np.random.shuffle(cell_colors)  # Mezclar colores
        theta_initial = np.random.rand(num_cells) * 2 * np.pi
        phi_initial = np.random.rand(num_cells) * np.pi
        r_cells_initial = np.random.rand(num_cells) * 1000
        return cell_colors, theta_initial, phi_initial, r_cells_initial
            
    # Función para crear esferas alargadas
    def create_elongated_sphere(x_center, y_center, z_center, elongation_factors, size):
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 10)
        x = size * elongation_factors[0] * np.outer(np.cos(u), np.sin(v)) + x_center
        y = size * elongation_factors[1] * np.outer(np.sin(u), np.sin(v)) + y_center
        z = size * elongation_factors[2] * np.outer(np.ones(np.size(u)), np.cos(v)) + z_center
        return x, y, z

    # Función para dibujar la esfera actual
    def draw_sphere(index):
        ax.clear()
        ax.set_xlim(-1200, 1200)
        ax.set_ylim(-1200, 1200)
        ax.set_zlim(-1200, 1200)
        
        # Obtener parámetros para la esfera actual
        c = params[index]['c']
        a = params[index]['a']
        t = params[index]['t']
        
        # Calcular las coordenadas de la esfera principal
        x_scaled = a * x
        y_scaled = a * y
        z_scaled = c * z
        
        # Dibujar solo el contorno de la esfera principal con baja opacidad
        ax.plot_wireframe(x_scaled, y_scaled, z_scaled, color='purple', alpha=0.04)
        
        # Inicializar el número de células basado en el tiempo
        num_cells = 15 + 15 * index  # 15, 30, 45, 60, 75, 90, 105
        cell_colors, theta_cells, phi_cells, r_cells_initial = initialize_cells(num_cells)
        
        # Parámetros para la forma elipsoidal de las minicélulas
        elongation_factor_x = 1.5  # Alarga en el eje x
        elongation_factor_y = 0.5  # Contrae en el eje y
        elongation_factor_z = 1.0  # Alarga en el eje z
        cell_size = 2500  # Tamaño de las células
        
        # Ajustar posiciones finales para cada color de célula
        r_cells_final = np.zeros(num_cells)
        scale_factor = (t - 24) / (168 - 24)
        
        for i, color in enumerate(cell_colors):
            if color == 'black':
                r_cells_final[i] = np.interp(scale_factor, [0, 1], [0.2 * a, 0.4 * a])
            elif color == 'orange':
                r_cells_final[i] = np.interp(scale_factor, [0, 1], [0.5 * a, 0.7 * a])
            elif color == 'blue':
                r_cells_final[i] = np.interp(scale_factor, [0, 1], [0.8 * a, a])
        
        # Interpolación progresiva entre posiciones iniciales y finales
        r_cells_interpolated = (1 - scale_factor) * r_cells_initial + scale_factor * r_cells_final
        
        # Reducir el rango de posiciones de las células sin cambiar su tamaño
        reduction_factor = 0.85
        r_cells_interpolated = np.clip(r_cells_interpolated * reduction_factor, 0, a)
        
        # Actualizar posiciones para las células
        x_cells = r_cells_interpolated * np.sin(phi_cells) * np.cos(theta_cells)
        y_cells = r_cells_interpolated * np.sin(phi_cells) * np.sin(theta_cells)
        z_cells = r_cells_interpolated * np.cos(phi_cells)
        
        # Asegurarse de que todas las células estén dentro de la esfera principal
        distances = np.sqrt(x_cells**2 + y_cells**2 + z_cells**2)
        mask = distances > a
        x_cells[mask] = x_cells[mask] * (a / distances[mask])
        y_cells[mask] = y_cells[mask] * (a / distances[mask])
        z_cells[mask] = z_cells[mask] * (a / distances[mask])
        
        # Dibujar las células internas con forma elipsoidal dentro de la esfera correspondiente
        for i in range(num_cells):
            x_center = x_cells[i]
            y_center = y_cells[i]
            z_center = z_cells[i]
            
            # Crear y dibujar la minicélula alargada usando plot_wireframe
            x_cell, y_cell, z_cell = create_elongated_sphere(x_center, y_center, z_center,
                                                            (elongation_factor_x, elongation_factor_y, elongation_factor_z), 
                                                            cell_size / 100)
            # Dibujar el contorno de las minicélulas
            ax.plot_wireframe(x_cell, y_cell, z_cell, color=cell_colors[i], alpha=0.6)

        # Ajustar el ángulo de visión
        ax.view_init(elev=20., azim=30)
        
        # Actualizar el canvas de tkinter
        canvas.draw()
        
        # Actualizar el texto con el estado actual
        instructions.config(text=f"""Muestra a la hora: {t} hrs
        \nAncho: {a:.2f}, Largo: {c:.2f}
        \nVolumen((4/3)pi*(a^2)*c): {(0.5)*a*a*c:.3f}
        \nVolumen2.0(Volumen/10^7): {(0.5*a*a*c)/100000000:.3f}
        \nUsa la flecha derecha para mostrar el siguiente crecimiento
        \nUsa la flecha izquierda para mostrar el crecimiento anterior""")
        number_label.config(text=f"Estado: {index + 1}/7")

    # Función para manejar las teclas de flecha
    def on_key(event):
        global current_index
        if event.keysym == 'Right':
            current_index = (current_index + 1) % len(params)
        elif event.keysym == 'Left':
            current_index = (current_index - 1) % len(params)
        draw_sphere(current_index)

    # Crear el canvas de Matplotlib y agregarlo a la ventana Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Llamar a la función para dibujar la esfera inicial
    draw_sphere(current_index)

    # Conectar la función de manejo de teclas
    root.bind('<Key>', on_key)

    # Iniciar el bucle de eventos de Tkinter
    root.mainloop()
    
if __name__ == "__main__":
    simulacion()