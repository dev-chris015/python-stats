import numpy as np
import matplotlib.pyplot as plt
import os
import time
import math

def run_simulation(max_N=1_000_000, num_tosses=12):
    print(f"\nIniciando simulación de Monte Carlo con N = {max_N:,} experimentos...\n")
    
    # Procesamiento por bloques para mostrar progreso
    chunk_size = min(max_N, max(1, max_N // 50))
    caras_counts = np.zeros(max_N, dtype=np.int8)
    
    print("Simulando los lanzamientos...")
    for i in range(0, max_N, chunk_size):
        end = min(i + chunk_size, max_N)
        size = end - i
        
        # Generar lanzamientos aleatorios para el bloque
        chunk_tosses = np.random.randint(0, 2, size=(size, num_tosses), dtype=np.int8)
        caras_counts[i:end] = np.sum(chunk_tosses, axis=1)
        
        # Barra de progreso en consola
        progress = int((end / max_N) * 50)
        bar = '█' * progress + '-' * (50 - progress)
        print(f"\r[{bar}] {end:,}/{max_N:,} experimentos ({int(end/max_N*100)}%)", end="", flush=True)
        time.sleep(0.02)  # Pequeña pausa para hacer visible el progreso
        
    print("\n\n¡Simulación completada con éxito!\n")
    
    # Mostrar resultados básicos
    count_12_caras = np.sum(caras_counts == num_tosses)
    count_12_escudos = np.sum(caras_counts == 0)
    
    prob_12_caras = count_12_caras / max_N
    prob_12_escudos = count_12_escudos / max_N
    p_teorica = (0.5)**num_tosses
    
    print("-" * 50)
    print("RESULTADOS DE LA SIMULACIÓN:")
    print("-" * 50)
    print(f"Probabilidad de 12 caras   : {prob_12_caras:.6f} (Teórico: {p_teorica:.6f})")
    print(f"Probabilidad de 12 escudos : {prob_12_escudos:.6f} (Teórico: {p_teorica:.6f})")
    print(f"Promedio de caras por exp  : {np.mean(caras_counts):.4f} (Teórico: {num_tosses/2:.4f})")
    print("-" * 50)
    
    # Generar el nuevo gráfico
    plot_new_results(caras_counts, num_tosses, max_N)

def plot_new_results(caras_counts, num_tosses, max_N):
    # Calcular frecuencias simuladas
    counts = np.bincount(caras_counts, minlength=num_tosses+1)
    sim_probs = counts / max_N
    
    # Calcular probabilidades teóricas (Distribución Binomial)
    x = np.arange(num_tosses + 1)
    theo_probs = np.array([math.comb(num_tosses, k) * (0.5**num_tosses) for k in x])
    
    # Configurar la figura (gráfico nuevo y diferente)
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#ffffff')
    
    width = 0.35
    
    # Barras de simulación
    rects1 = ax.bar(x - width/2, sim_probs, width, label='Simulación Monte Carlo', 
                    color='#3b82f6', edgecolor='black', alpha=0.8)
    
    # Barras teóricas
    rects2 = ax.bar(x + width/2, theo_probs, width, label='Teórico (Binomial)', 
                    color='#ef4444', edgecolor='black', alpha=0.8)
    
    # Línea de tendencia teórica
    ax.plot(x, theo_probs, color='#1f2937', marker='o', linestyle='dashed', 
            linewidth=2, label='Curva Teórica')
    
    # Títulos y etiquetas
    ax.set_xticks(x)
    ax.set_xlabel(f'Número de Caras obtenidas en {num_tosses} lanzamientos', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probabilidad de Ocurrencia', fontsize=12, fontweight='bold')
    ax.set_title('Distribución de Resultados: Simulación vs Teoría Binomial', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Añadir valores exactos sobre las barras más altas
    for i in range(len(x)):
        if sim_probs[i] > 0.05:
            ax.text(x[i] - width/2, sim_probs[i] + 0.005, f'{sim_probs[i]:.3f}', 
                    ha='center', va='bottom', fontsize=9, rotation=45)
            
    plt.tight_layout()
    
    # Guardar la nueva gráfica
    output_path = os.path.join(os.path.dirname(__file__), 'grafico_distribucion_binomial.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n[+] Nuevo gráfico guardado exitosamente en:\n    {output_path}\n")

def get_user_inputs():

    # Pedir número de experimentos
    default_N = 1_000_000
    prompt_N = f"Ingrese el número de experimentos, se definen 1,000,000 por defecto: "
    try:
        user_input = input(prompt_N).strip()
        if not user_input:
            max_N = default_N
        else:
            max_N = int(float(user_input.replace('_', '')))
            if max_N <= 0:
                print("Valor inválido. Usando por defecto.")
                max_N = default_N
    except (ValueError, OverflowError):
        print("Entrada no válida, usaremos valor por defecto.")
        max_N = default_N
        
    print(f"-> Experimentos configurados en: {max_N:,}")
    return max_N

if __name__ == '__main__':
    max_N = get_user_inputs()
    run_simulation(max_N=max_N, num_tosses=12)

