import numpy as np
import matplotlib.pyplot as plt
import os
import time
import math
import random

def run_simulation(max_N=1_000_000, num_tosses=12):
    print(f"\nIniciando Análisis de {num_tosses} Caras...")
    
    # Distribución Binomial (Caras en N lanzamientos)
    print(f"\n[1/2] Simulando Distribución Binomial")
    chunk_size = min(max_N, max(1, max_N // 20))
    caras_counts = np.zeros(max_N, dtype=np.int8)
    
    for i in range(0, max_N, chunk_size):
        end = min(i + chunk_size, max_N)
        size = end - i
        chunk_tosses = np.random.randint(0, 2, size=(size, num_tosses), dtype=np.int8)
        caras_counts[i:end] = np.sum(chunk_tosses, axis=1)
        
        progress = int((end / max_N) * 20)
        bar = '█' * progress + '-' * (20 - progress)
        print(f"\r[{bar}] {end:,}/{max_N:,}", end="", flush=True)
    print("----> Completado")

    # racha continua
    # Limitamos N para esta simulación porque es muy pesada (esperanza matemática = 8190 lanzamientos por exp)
    N_racha = min(max_N, 10_000) 
    print(f"\n[2/2] Simulando Racha Continua de {num_tosses} caras")
    
    intentos_racha = np.zeros(N_racha, dtype=np.int32)
    chunk_racha = max(1, N_racha // 20)
    
    for i in range(N_racha):
        lanzamientos = 0
        racha = 0
        while racha < num_tosses:
            lanzamientos += 1
            if random.random() < 0.5:
                racha += 1
            else:
                racha = 0
        intentos_racha[i] = lanzamientos
        
        if (i + 1) % chunk_racha == 0 or (i + 1) == N_racha:
            progress = int(((i + 1) / N_racha) * 20)
            bar = '█' * progress + '-' * (20 - progress)
            print(f"\r[{bar}] {i+1:,}/{N_racha:,}", end="", flush=True)
    print("----> Completado")

    # Resultados en texto
    prob_12_caras = np.sum(caras_counts == num_tosses) / max_N
    p_teorica = (0.5)**num_tosses
    promedio_racha = np.mean(intentos_racha)
    esperanza_racha = (2**(num_tosses+1)) - 2

    print("Resultado de la simulacion:")
    print("-"*60)
    print("Lanzar 12 veces por experimento")
    print(f" - Prob. de obtener 12 caras : {prob_12_caras:.6f} - Teórico: {p_teorica:.6f}")
    print(f" - Promedio de caras por exp : {np.mean(caras_counts):.4f} - Teórico: {num_tosses/2:.4f}")
    print("\nLanzar hasta obtener 12 caras seguidas")
    print(f" - Promedio de intentos req. : {promedio_racha:,.1f} - Teórico: {esperanza_racha:,.1f}")
    print("-"*60)
    
    # Generar el nuevo gráfico doble
    plot_combined_results(caras_counts, intentos_racha, num_tosses, max_N, N_racha, esperanza_racha)

def plot_combined_results(caras_counts, intentos_racha, num_tosses, max_N, N_racha, esperanza_racha):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('#f8f9fa')
    
    # GRAFICO 1: Distribución del Tiempo de Espera (Racha Continua)
    ax1.set_facecolor('#ffffff')
    bins = np.linspace(0, np.percentile(intentos_racha, 95), 40)
    ax1.hist(intentos_racha, bins=bins, color='#10b981', edgecolor='black', alpha=0.8, density=True)
    ax1.axvline(esperanza_racha, color='#ef4444', linestyle='dashed', linewidth=2, 
                label=f'Promedio Teórico ({esperanza_racha:,.0f})')
    
    ax1.set_xlabel('Intentos necesarios', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Densidad', fontsize=11, fontweight='bold')
    ax1.set_title(f'¿Cuántos intentos para {num_tosses} caras seguidas?', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.6)

    # ---------------------------------------------------------
    # GRAFICO 2: Distribución Binomial (Caras en 12 lanzamientos)
    # ---------------------------------------------------------
    ax2.set_facecolor('#ffffff')
    counts = np.bincount(caras_counts, minlength=num_tosses+1)
    sim_probs = counts / max_N
    x = np.arange(num_tosses + 1)
    theo_probs = np.array([math.comb(num_tosses, k) * (0.5**num_tosses) for k in x])
    
    width = 0.35
    ax2.bar(x - width/2, sim_probs, width, label='Simulación', color='#3b82f6', edgecolor='black', alpha=0.8)
    ax2.bar(x + width/2, theo_probs, width, label='Teórico (Binomial)', color='#ef4444', edgecolor='black', alpha=0.8)
    ax2.plot(x, theo_probs, color='#1f2937', marker='o', linestyle='dashed', linewidth=2)
    
    ax2.set_xticks(x)
    ax2.set_xlabel(f'Número de Caras en {num_tosses} lanzamientos', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Probabilidad', fontsize=11, fontweight='bold')
    ax2.set_title(f'Distribución de Caras (Binomial)', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.6)

    plt.tight_layout(pad=3.0)
    output_path = os.path.join(os.path.dirname(__file__), 'grafico_analisis_combinado.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    #print(f"\n[+] Gráfico combinado guardado en:\n    {output_path}\n")

def get_user_inputs():
    default_N = 1_000_000
    prompt_N = f"Ingrese el número de experimentos, se definen 1,000,000 por defecto: "
    try:
        user_input = input(prompt_N).strip()
        if not user_input:
            max_N = default_N
        else:
            max_N = int(float(user_input.replace('_', '')))
            if max_N <= 0:
                max_N = default_N
    except:
        max_N = default_N
        
    return max_N

if __name__ == '__main__':
    max_N = get_user_inputs()
    run_simulation(max_N=max_N, num_tosses=12)

