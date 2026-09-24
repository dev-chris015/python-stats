import numpy as np
import matplotlib.pyplot as plt
import os

def run_simulation(max_N=1_000_000, num_tosses=12):
    # Simulacion de Monte Carlo para la probabilidad de obtener 12 caras o 12 escudos
    # Escala logarítmica para ver la convergencia
    N_values = [10**i for i in range(1, int(np.log10(max_N)) + 1)]
    if max_N not in N_values:
        N_values.append(max_N)
        
    print(f"Iniciando simulación de Monte Carlo hasta N = {max_N:,}...\n")
    
    # Probabilidad teórica de obtener 12 caras o 12 escudos
    p_12_same = (0.5)**num_tosses 
    avg_expected = num_tosses * 0.5
    
    results = {
        'N': [],
        'p_12_caras': [],
        'p_12_escudos': [],
        'avg_caras': [],
        'avg_escudos': []
    }
    
    print("Generando matriz de lanzamientos vectorizada")
    # Generar todos los lanzamientos de una vez (memoria eficiente con int8)
    tosses = np.random.randint(0, 2, size=(max_N, num_tosses), dtype=np.int8)
    
    # Calcular sumas por experimento (1s = caras)
    caras_counts = np.sum(tosses, axis=1)
    escudos_counts = num_tosses - caras_counts
    
    print("\n| N          | P-12 Caras | Error Abs  | P-12 Escudos | Error Abs  | Prom Caras | Prom Escudos |")
    print("-" * 97)
    
    for n in N_values:
        # Tomar el subconjunto de simulaciones hasta n
        sub_caras = caras_counts[:n]
        sub_escudos = escudos_counts[:n]
        
        # Calcular proporciones de rachas completas
        count_12_caras = np.sum(sub_caras == num_tosses)
        prob_12_caras = count_12_caras / n
        
        count_12_escudos = np.sum(sub_escudos == num_tosses)
        prob_12_escudos = count_12_escudos / n
        
        # Calcular promedios
        avg_caras_val = np.mean(sub_caras)
        avg_escudos_val = np.mean(sub_escudos)
        
        results['N'].append(n)
        results['p_12_caras'].append(prob_12_caras)
        results['p_12_escudos'].append(prob_12_escudos)
        results['avg_caras'].append(avg_caras_val)
        results['avg_escudos'].append(avg_escudos_val)
        
        err_c = abs(prob_12_caras - p_12_same)
        err_e = abs(prob_12_escudos - p_12_same)
        
        print(f"| {n:<10,} | {prob_12_caras:.6f}    | {err_c:.6f}   | {prob_12_escudos:.6f}    | {err_e:.6f}   | {avg_caras_val:.4f}     | {avg_escudos_val:.4f}     |")

    print("-" * 97)
    print(f"Valor Teórico para 12 intentos seguidos iguales = {p_12_same:.6f}")
    print(f"Valor Teórico Promedio     = {avg_expected:.4f}")
    
    plot_results(results, p_12_same, avg_expected)

def plot_results(results, p_12_same, avg_expected):
    N_vals = results['N']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Subplot 1: Probabilidad de 12 seguidos
    ax1.plot(N_vals, results['p_12_caras'], marker='o', label='Simulación 12 Caras', color='royalblue')
    ax1.plot(N_vals, results['p_12_escudos'], marker='s', label='Simulación 12 Escudos', color='forestgreen')
    ax1.axhline(y=p_12_same, color='crimson', linestyle='--', label=f'Teórico ({p_12_same:.6f})')
    ax1.set_xscale('log')
    ax1.set_xlabel('Número de Experimentos (N) - Escala Log')
    ax1.set_ylabel('Probabilidad Estimada')
    ax1.set_title('Convergencia: Probabilidad de 12 Caras o 12 Escudos')
    ax1.legend()
    ax1.grid(True, which="both", ls="--", alpha=0.6)
    
    # Subplot 2: Promedio en 12 lanzamientos
    ax2.plot(N_vals, results['avg_caras'], marker='o', label='Promedio Caras', color='royalblue')
    ax2.plot(N_vals, results['avg_escudos'], marker='s', label='Promedio Escudos', color='forestgreen')
    ax2.axhline(y=avg_expected, color='crimson', linestyle='--', label=f'Teórico ({avg_expected:.1f})')
    ax2.set_xscale('log')
    ax2.set_xlabel('Número de Experimentos (N) - Escala Log')
    ax2.set_ylabel('Promedio por Experimento de 12')
    ax2.set_title('Convergencia: Promedio de Lanzamientos')
    ax2.legend()
    ax2.grid(True, which="both", ls="--", alpha=0.6)
    
    plt.tight_layout()
    
    output_path = os.path.join(os.path.dirname(__file__), 'grafico_convergencia.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
   # print(f"\nGráfico guardado exitosamente en: {output_path}")

def get_user_N(default_N=1_000_000):

    prompt = f"Ingrese el número máximo de experimentos, ENTER para valor por defecto {default_N:,}: "
    try:
        user_input = input(prompt).strip()
        if not user_input:
            print(f"Usando valor por defecto: {default_N:,} experimentos.\n")
            return default_N
        
        # Soportar formatos como 1_000_000 o 1e6
        val = int(float(user_input.replace('_', '')))
        if val <= 0:
            print(f"El número debe ser mayor a 0, usaremos valor por defecto: {default_N:,} experimentos.\n")
            return default_N
        
        print(f" Experimentos configurados en: {val:,}\n")
        return val
    except (ValueError, OverflowError):
        print(f" Entrada no válida, usaremos valor por defecto: {default_N:,} experimentos.\n")
        return default_N

if __name__ == '__main__':
    max_N = get_user_N(default_N=1_000_000)
    run_simulation(max_N=max_N, num_tosses=12)

