import time        # se usa para medir el tiempo de ejecucion del algoritmo CYK
import subprocess  # se usa para llamar al ejecutable bison_parser desde Python
import matplotlib  # libreria principal de graficas
matplotlib.use('Agg')  # backend sin ventana para guardar PNG sin abrir interfaz grafica
import matplotlib.pyplot as plt  # se usa para dibujar y guardar las graficas
import psutil      # se usa para medir el uso de memoria RAM
import os          # se usa para obtener el proceso actual y medir su memoria

# ─── TAMAÑOS DE PRUEBA ───────────────────────────────────────────────────────
# cada numero representa cuantos "10" se unen con "+" para formar la expresion
TAMANOS = [39, 199, 599]

# ─── GRAMATICA EN CNF PARA CYK ──────────────────────────────────────────────
# la gramatica esta en Forma Normal de Chomsky (CNF) que CYK necesita
# E -> E P | num
# P -> A E
# A -> +
GRAMATICA = {
    "E": [["E", "P"], ["num"]],  # E puede ser E seguido de P, o un numero
    "P": [["A", "E"]],           # P es un operador A seguido de E
    "A": [["+"]]                 # A es el operador suma
}


def cyk_parser(tokens, gramatica):
    # funcion que implementa el algoritmo CYK para verificar si los tokens son validos
    n = len(tokens)  # cantidad total de tokens en la expresion
    if n == 0:       # si no hay tokens, la expresion es invalida
        return False

    # se crea la tabla de programacion dinamica de tamanio n x n
    tabla = [[set() for _ in range(n - l + 1)] for l in range(1, n + 1)]

    # se llena la diagonal con los terminales (tokens individuales)
    for i in range(n):  # se recorre cada token de la expresion
        for lhs, rhs_list in gramatica.items():  # se revisan todas las reglas
            for rhs in rhs_list:  # se revisa cada produccion de la regla
                if len(rhs) == 1 and rhs[0] == "num":  # si es un terminal "num"
                    tabla[0][i].add(lhs)  # se agrega el no terminal a la celda

    # se llena el resto de la tabla combinando subcadenas
    for l in range(2, n + 1):          # l es la longitud de la subcadena
        for s in range(n - l + 1):     # s es la posicion de inicio
            for p in range(1, l):      # p es el punto de division
                for lhs, rhs_list in gramatica.items():  # se revisan las reglas
                    for rhs in rhs_list:  # se revisa cada produccion
                        if len(rhs) == 2:  # solo reglas binarias (CNF)
                            B, C = rhs     # se separan los dos no terminales
                            if B in tabla[p-1][s] and C in tabla[l-p-1][s+p]:
                                tabla[l-1][s].add(lhs)  # se agrega si ambos coinciden

    return "E" in tabla[n-1][0]  # la expresion es valida si E cubre toda la cadena


def medir_memoria_proceso():
    # retorna la memoria RAM usada por el proceso actual en MB
    proceso = psutil.Process(os.getpid())  # se obtiene el proceso de Python actual
    return proceso.memory_info().rss / 1024 / 1024  # se convierte de bytes a MB


def correr_bison(expresion):
    # llama al ejecutable bison_parser y retorna el tiempo que reporta en ms
    resultado = subprocess.run(
        ['./bison_parser'],           # ejecutable compilado de Bison
        input=expresion,              # se le pasa la expresion por stdin
        capture_output=True,          # se captura la salida
        text=True                     # se lee como texto
    )
    # si bison retorno un numero valido se convierte a float, si no retorna 0
    return float(resultado.stdout.strip()) if resultado.stdout.strip() else 0.0


def main():
    # listas donde se guardan los resultados de cada tamano
    tiempos_bison  = []  # tiempos de Bison en ms
    tiempos_cyk    = []  # tiempos de CYK en ms
    memoria_bison  = []  # RAM de Bison en MB
    memoria_cyk    = []  # RAM de CYK en MB
    tokens_totales = []  # cantidad de tokens por tamano

    # ── Tabla 1: tiempo ──────────────────────────────────────────────────────
    print(f"\n{'LONGITUD':<15} {'BISON (ms)':<15} {'CYK (ms)':<15}")
    print("-" * 45)

    for n in TAMANOS:  # se recorre cada tamano de prueba
        expresion = " + ".join(["10"] * n)  # se construye la expresion con n numeros
        tokens_cyk = ["num", "+"] * (n - 1) + ["num"]  # se generan los tokens para CYK
        tokens_totales.append(len(tokens_cyk))  # se guarda la cantidad de tokens

        # medir Bison
        t_bison = correr_bison(expresion)  # se llama a bison y se mide el tiempo
        tiempos_bison.append(t_bison)      # se guarda el tiempo de Bison

        # medir CYK
        inicio = time.perf_counter()                    # se inicia el cronometro
        cyk_parser(tokens_cyk, GRAMATICA)               # se corre el algoritmo CYK
        t_cyk = (time.perf_counter() - inicio) * 1000  # se convierte a milisegundos
        tiempos_cyk.append(t_cyk)                       # se guarda el tiempo de CYK

        print(f"{len(tokens_cyk):<15} {t_bison:<15.4f} {t_cyk:<15.4f}")  # se imprime la fila

    # ── Tabla 2: memoria ─────────────────────────────────────────────────────
    print(f"\n{'TOKENS':<15} {'BISON (ms)':<12} {'RAM B (MB)':<12} {'CYK (ms)':<12} {'RAM C (MB)':<12}")
    print("-" * 63)

    for i, n in enumerate(TAMANOS):  # se recorre cada tamano de prueba
        expresion  = " + ".join(["10"] * n)   # se construye la expresion
        tokens_cyk = ["num", "+"] * (n - 1) + ["num"]  # tokens para CYK

        # memoria Bison — se mide antes y despues de llamar al proceso
        mem_antes  = medir_memoria_proceso()        # RAM antes de correr Bison
        t_bison    = correr_bison(expresion)        # se corre Bison
        mem_bison  = medir_memoria_proceso()        # RAM despues de correr Bison
        ram_bison  = max(mem_bison - mem_antes, 0)  # diferencia de RAM usada
        memoria_bison.append(ram_bison)             # se guarda

        # memoria CYK
        mem_antes = medir_memoria_proceso()                    # RAM antes de CYK
        inicio    = time.perf_counter()                        # cronometro
        cyk_parser(tokens_cyk, GRAMATICA)                      # se corre CYK
        t_cyk     = (time.perf_counter() - inicio) * 1000     # tiempo en ms
        ram_cyk   = medir_memoria_proceso() - mem_antes        # RAM usada por CYK
        ram_cyk   = max(ram_cyk, 0)                            # no puede ser negativa
        memoria_cyk.append(ram_cyk)                            # se guarda

        print(f"{tokens_totales[i]:<15} {tiempos_bison[i]:<12.4f} {ram_bison:<12.2f} {t_cyk:<12.4f} {ram_cyk:<12.2f}")

    # ── Grafica 1: rendimiento (tiempo) ──────────────────────────────────────
    plt.figure(figsize=(10, 6))  # se crea la figura con tamano 10x6 pulgadas
    plt.plot(tokens_totales, tiempos_cyk,   'r-o', linewidth=2, label='CYK  O(n^3)')   # curva CYK en rojo
    plt.plot(tokens_totales, tiempos_bison, 'b-s', linewidth=2, label='Bison LALR O(n)')  # curva Bison en azul
    plt.yscale('log')  # escala logaritmica para ver ambas curvas aunque sean muy diferentes
    plt.title('Comparativa de Rendimiento — Tiempo de Ejecucion')  # titulo de la grafica
    plt.xlabel('Cantidad de Tokens en la Expresion')   # etiqueta del eje X
    plt.ylabel('Tiempo (ms) — Escala Logaritmica')     # etiqueta del eje Y
    plt.legend()                                        # se muestra la leyenda
    plt.grid(True, which="both", ls="--", alpha=0.4)   # se agrega la grilla
    plt.tight_layout()                                  # se ajustan los margenes
    plt.savefig('grafica_rendimiento.png', dpi=150)     # se guarda la imagen
    plt.close()  # se cierra la figura para liberar memoria
    print("\nGrafica guardada: grafica_rendimiento.png")

    # ── Grafica 2: memoria RAM ────────────────────────────────────────────────
    plt.figure(figsize=(10, 6))  # nueva figura para la grafica de memoria
    plt.plot(tokens_totales, memoria_cyk,   'r-o', linewidth=2, label='CYK  — RAM')    # RAM de CYK
    plt.plot(tokens_totales, memoria_bison, 'b-s', linewidth=2, label='Bison — RAM')   # RAM de Bison
    plt.title('Comparativa de Memoria RAM')         # titulo
    plt.xlabel('Cantidad de Tokens en la Expresion')  # eje X
    plt.ylabel('Memoria RAM usada (MB)')              # eje Y
    plt.legend()                                      # leyenda
    plt.grid(True, ls="--", alpha=0.4)                # grilla
    plt.tight_layout()                                # margenes
    plt.savefig('comparativa_memoria.png', dpi=150)   # se guarda
    plt.close()  # se cierra la figura
    print("Grafica guardada: comparativa_memoria.png")

    # ── Grafica 3: final combinada ────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))  # dos paneles lado a lado

    # panel izquierdo — tiempo
    ax1.plot(tokens_totales, tiempos_cyk,   'r-o', linewidth=2, label='CYK  O(n^3)')
    ax1.plot(tokens_totales, tiempos_bison, 'b-s', linewidth=2, label='Bison LALR O(n)')
    ax1.set_yscale('log')                              # escala log
    ax1.set_title('Tiempo de Ejecucion (ms)')          # titulo del panel
    ax1.set_xlabel('Cantidad de Tokens')               # eje X
    ax1.set_ylabel('Tiempo (ms) — Escala Log')         # eje Y
    ax1.legend()                                       # leyenda
    ax1.grid(True, which="both", ls="--", alpha=0.4)  # grilla

    # panel derecho — memoria
    ax2.plot(tokens_totales, memoria_cyk,   'r-o', linewidth=2, label='CYK  — RAM')
    ax2.plot(tokens_totales, memoria_bison, 'b-s', linewidth=2, label='Bison — RAM')
    ax2.set_title('Uso de Memoria RAM (MB)')   # titulo del panel
    ax2.set_xlabel('Cantidad de Tokens')        # eje X
    ax2.set_ylabel('Memoria RAM (MB)')          # eje Y
    ax2.legend()                                # leyenda
    ax2.grid(True, ls="--", alpha=0.4)          # grilla

    fig.suptitle('Comparativa General: Bison LALR vs CYK', fontsize=14, fontweight='bold')  # titulo general
    plt.tight_layout()                          # se ajustan los margenes
    plt.savefig('grafica_final.png', dpi=150)   # se guarda la grafica final
    plt.close()  # se cierra
    print("Grafica guardada: grafica_final.png")
    print("\nProceso finalizado. Se generaron 3 graficas y 2 tablas.")


if __name__ == "__main__":
    main()  # se ejecuta la funcion principal
